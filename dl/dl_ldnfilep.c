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
** dl_ldnfilep - Load any file, into private shm segments.
*/

#define _auxtemp _auxtemp2	/* A bug in ldfcn.h */

#include <stdio.h>
#include <filehdr.h>
#include <syms.h>
#include <ar.h>
#include <ldfcn.h>
#include <scnhdr.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#include "dl.h"

static void *allocseg();
static setsegro();


#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif /* DEBUG */

dl_ldnfilep(ldptr)
    LDFILE *ldptr;
{
    int i, nsect;
    int tsize = 0, dsize = 0;
    unsigned taddr = 0xffffffff, daddr = 0xffffffff;
    void *tseg, *dseg;
    struct scnhdr shdr;
    int tsegid;

    /*
    ** Make a first pass over the sections, and compute total text
    ** and data segment sizes.
    */
    nsect = HEADER(ldptr).f_nscns;
    D(printf("loadfile: %d sections\n", nsect));
    for ( i=1; i<nsect+1; i++ ) {
	if ( ldshread(ldptr, i, &shdr) == FAILURE ) {
	    dl_error("Cannot read section header %d", i);
	    return 0;
	}
	D(printf("loadfile: section %d=%s, 0x%x:0x%x@0x%x type 0x%x\n", i,
	       shdr.s_name, shdr.s_vaddr, shdr.s_size, shdr.s_scnptr, shdr.s_flags));
	/*
	** We would like to use the lower 4 bits in s_flags here to decide
	** what to do with the segment (allocate/load), but they don't seem
	** to be set correctly. So, we have to fiddle.
	*/
	switch(shdr.s_flags) {
	case STYP_TEXT:
	    if ( tsize ) {
		dl_error("Multiple text segments?", 0);
		return 0;
	    }
	    tsize += shdr.s_size;
	    if ( taddr > shdr.s_vaddr ) taddr = shdr.s_vaddr;
	    break;
	case STYP_DATA:
	case STYP_BSS:
	case STYP_RDATA:
	case STYP_SDATA:
	case STYP_SBSS:
	case STYP_LIT8:
	case STYP_LIT4:
	    dsize += shdr.s_size;
	    if ( daddr > shdr.s_vaddr ) daddr = shdr.s_vaddr;
	    break;
	case _STYP_RESOURCE:
	    break;                   /* Ignore this one */
	default:
	    if(  shdr.s_flags & STYP_COMMENT ) {
		D(printf("Skipping comment section %x\n", shdr.s_flags));
		break;
	    }
	    dl_error("Unknown section type 0x%x", shdr.s_flags);
	    return 0;
	}
    }
    /*
    ** We now know the sizes. Allocate the segments.
    */
    D(printf("Textaddr: 0x%x, dataaddr: 0x%x\n", taddr, daddr));
    D(printf("Textsize: 0x%x, datasize: 0x%x\n", tsize, dsize));
    if ( (tseg = allocseg(taddr, tsize, &tsegid)) == 0 )
      return 0;
    if ( dsize ) {
	if ( (dseg = allocseg(daddr, dsize, (int *)0)) == 0 )
	  return 0;
    }
    /*
    ** Next, we make another pass over the sections and load the data
    ** (or zero the section, for bss sections).
    */
    for(i=1; i<nsect+1; i++) {
	if ( ldshread(ldptr, i, &shdr) == FAILURE) {
	    dl_error("Cannot read section header %d", i);
	    return 0;
	}
	if ( shdr.s_scnptr ) {
	    D(printf ( "Read sect %d\n", i));
	    if ( ldsseek(ldptr, i) == FAILURE ) {
		dl_error("Cannot seek to data for section %d", i);
	        return 0;
	    }
	    D(printf ("At address %x\n", ftell(IOPTR(ldptr))));
	    if ( FREAD((void *)shdr.s_vaddr, 1, shdr.s_size, ldptr) != shdr.s_size ) {
		dl_error("Cannot read data for section %d", i);
	        return 0;
	    }
	} else {
	    bzero((char *)shdr.s_vaddr, shdr.s_size);
	    D(printf("Skip sect %d\n", i));
	}
    }
    /*
    ** Step 5 - Make text segment read/only.
    */
    if ( setsegro(tseg, tsegid) == 0 ) {
        return 0;
    }
    return 1;
}

static void *
allocseg(addr, len, id)
    unsigned addr, len;
    int *id;
{
    int shmid;
    void *rv;

    if ( !dl_setrange(addr, addr+len) ) {
	dl_error("Segment does not fit. Try calling dl_setsegsizeguess(0x%x)",
		 len);
	return 0;
    }
    shmid = shmget(IPC_PRIVATE, len, 0777);
    D(printf("shmget=%x\n", shmid));
    if ( shmid < 0 ) {
	dl_error(0, "shmget");
        return 0;
    }
    rv = shmat(shmid, (void *)addr, SHM_RND);
    if ((int)rv == -1) {
	dl_error(0, "shmat");
        return 0;
    }
    if ( id ) {
	*id = shmid;
    } else {
	shmctl(shmid, IPC_RMID);
    }
    D(printf("shmat=%x\n", rv));
    return rv;
}

static setsegro(tseg, tsegid)
    void *tseg;
    int tsegid;
{
    shmdt(tseg);
    D(printf("setsegro ( %x, %d)\n", tseg, tsegid));
    if( shmat(tsegid, tseg, SHM_RDONLY|SHM_RND) != tseg ) {
	dl_error(0, "shmat(read-only text segment)");
        return 0;
    }
    shmctl(tsegid, IPC_RMID);
    return 1;
}
