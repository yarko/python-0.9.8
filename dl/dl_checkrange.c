/***********************************************************
Copyright 1991 by Stichting Mathematisch Centrum, Amsterdam, The
Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, 
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in 
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

******************************************************************/
/*
** dl_checkrange - Check that a given address range is free.
*/
#include "dl.h"
#include <string.h>

#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif /* DEBUG */

/* Macro's to handle bitmaps */
#define IND(x) ((x)>>5)
#define BIT(x) ((x)&0x1f)

#define ISSET(map,x) (map[IND(x)] & (1<<BIT(x)))
#define DOSET(map,x) (map[IND(x)] |= (1<<BIT(x)))

/* Macros to convert addresses to segment indices */
#define SEGSIZE 0x00400000		/* 4Mb segsize */
#define BTOS(x) ((x)/SEGSIZE)

#define MAXADDR 0x7fffffff		/* Max user address */
#define NSEG	(BTOS(MAXADDR)+1)	/* Number of segments */

/* Other stuff */
#define MINTEXTADDR	0x00400000	/* Min text address */
#define MAXTEXTADDR	0x0bffffff
#define MINLIBADDR	0x0c000000	/* Where shared libs are loaded */
#define MAXLIBADDR	0x0fffffff
#define MINDATAADDR	0x10000000	/* Where normal data is loaded */
#define MAXDATAADDR	0x7fffffff	
#define HEADROOM	0x01000000	/* Headroom for data space */

#define NINRANGE(min, max) ((max-min)/SEGSIZE)

/* The map */
long map[IND(NSEG)];
int map_inited;

static
initmap() {
    extern etext, end;
    long i;

    if ( map_inited ) return;
    D(printf("Initializing map, size %d\n", IND(NSEG)));
    for ( i=0; i<=(long)&etext; i+=SEGSIZE)
      DOSET(map, BTOS(i));
    for ( i=MINLIBADDR; i<=MAXLIBADDR; i+=SEGSIZE)
      DOSET(map, BTOS(i));
    for ( i=MINDATAADDR; i<(long)&end+HEADROOM; i+=SEGSIZE)
      DOSET(map, BTOS(i));
    map_inited = 1;
}

static
findfree(min, max, pref, len)
    long min, max, pref, len;
{
    long try = pref;
    long tlen;

    if ( try % SEGSIZE ) {
	dl_error("Internal error: non-aligned address in checkrange", 0);
	return 0;
    }
    while(1) {
	/* Find a free slot where we can start to search */
	while( ISSET(map, BTOS(try))) {
	    try+=SEGSIZE;
	    if ( try >= max ) try = min;
	    if ( try == pref ) return 0;
	}
	/* If there's a chance of fitting it here see if the range is free */
	if ( try + len <= max ) {
	    tlen = 0;
	    while ( !ISSET(map, BTOS(try+tlen)) ) {
		if ( tlen >= len ) return try;
		tlen += SEGSIZE;
	    }
	}
    }
}

void *
dl_getrange(len)
    long len;
{
    long addr;

    addr = findfree(MINDATAADDR, MAXDATAADDR, MINDATAADDR, len);
    if ( dl_setrange(addr, addr+len) == 0 ) {
	dl_error("Internal error: findfree returned used region", 0);
	return 0;
    }
    return (void *)addr;
}

dl_checkrange(beg, end)
    long beg, end;
{
    long a;

    D(printf("Checkrange(%x to %x)\n", beg, end));
    initmap();
    for( a=beg; a<=end; a += SEGSIZE )
      if ( ISSET(map, BTOS(a)) )
	return 0;
    return 1;
}

dl_setrange(beg, end)
    long beg, end;
{
    long a;

    D(printf("Setrange(%x to %x)\n", beg, end));
    initmap();
    for ( a=beg; a<=end; a += SEGSIZE ) {
	if ( ISSET(map, BTOS(a)) ) {
	    return 0;
	}
	DOSET(map, BTOS(a));
    }
    return 1;
}

int
dl_hashaddrs(name, tlen, dlen, taddrp, daddrp)
    char *name;
    long tlen, dlen;
    long *taddrp, *daddrp;
{
    unsigned long hashval;
    long taddr, daddr;
    int i;
    char *p;

    initmap();
    hashval = 0;
    p = strrchr(name, '/');
    if ( p == 0 ) p = name;
    D(printf("dl_hashaddrs(%s(%s), %x, %x)\n", name, p, tlen, dlen));
    for(i=0; name[i]; i++)
      hashval += name[i]*i;
    taddr = (hashval%NINRANGE(MINTEXTADDR, MAXTEXTADDR))*SEGSIZE + MINTEXTADDR;
    daddr = (hashval%NINRANGE(MINDATAADDR, MAXDATAADDR))*SEGSIZE + MINDATAADDR;
    D(printf("dl_hashaddrs: 0x%x, 0x%x\n", taddr, daddr));
    taddr = findfree(MINTEXTADDR, MAXTEXTADDR, taddr, tlen);
    daddr = findfree(MINDATAADDR, MAXDATAADDR, daddr, dlen);
    D(printf("dl_hashaddrs: using 0x%x 0x%x\n", taddr, daddr));
    if ( taddr == 0 || daddr == 0 ) return 0;
    *taddrp = taddr;
    *daddrp = daddr;
    return 1;
}
