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
** dl_findcache - See if a cached binary is up-to-date
*/

#define _auxtemp _auxtemp5	/* Bug in ldfcn.h */
#include <stdio.h>
#include <aouthdr.h>
#include <filehdr.h>
#include <syms.h>
#include <ar.h>
#include <ldfcn.h>
#include <stdlib.h>

#include "dl.h"

#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif

#define NREMOVE 32

static char *toberemoved[NREMOVE];
static char **toberemovedp = toberemoved;

static char cachebuf[1030];

void
dl_remove_tmp() {
    D(printf("dl_remove_tmp: removing tempfiles\n"));
    while ( --toberemovedp >= toberemoved ) {
	D(printf("removing %s\n", *toberemovedp));
	unlink(*toberemovedp);
    }
}

int
dl_findcache(obj, ostamp, cname)
    char *obj, **cname;
    int ostamp;
{
    int stamp;
    LDFILE *ldptr;
    AOUTHDR aouth;
    int fd;
    char *tname;
    
    *cname = cachebuf;
    strncpy(cachebuf, obj, 1024);
    if ( strncmp(cachebuf+strlen(cachebuf)-2, ".o", 2) == 0)
      cachebuf[strlen(cachebuf)-2] = 0;
    strcat(cachebuf, ".ld");
    if ( access(cachebuf, 0) == 0 && (ldptr=ldopen(cachebuf, 0)) != 0) {
	D(printf("Found cached file\n"));
	stamp = SYMHEADER(ldptr).vstamp;
	if ( ldohseek(ldptr) == FAILURE ) {
	    D(printf("Cannot seek to a.out header on %s\n", cachebuf));
	    ldclose(ldptr);
	    goto bad;
	}
	if ( FREAD((char *)&aouth, 1, sizeof(aouth), ldptr) != sizeof(aouth) ) {
	    D(printf("Cannot read a.out header from %s\n", cachebuf));
	    ldclose(ldptr);
	    goto bad;
	}
	if ( ! dl_checkrange(aouth.text_start, aouth.text_start+aouth.tsize) ||
	     ! dl_checkrange(aouth.data_start, aouth.data_start
			     + aouth.dsize+aouth.bsize) ) {
	    D(printf("Addresses in use: T %x %x, D %x %x\n", aouth.text_start,\
		     aouth.tsize, aouth.data_start, aouth.dsize+aouth.bsize));
	    ldclose(ldptr);
	    goto bad;
	}
	ldclose(ldptr);
	if ( (unsigned short)stamp == (unsigned short)ostamp ) {
	    /* They match! The .ld file was created from the current file */
	    /*XXXX Should also check that addresses are OK */
	    D(printf("And timestamp ok\n"));
	    return 1;
	}
	D(printf("But wrong timestamp, wtd %x, got %x\n", ostamp, stamp));
    }
bad:
    D(printf("No correct cached file, trying to create one\n"));
    /* Doesn't exist yet, or incorrect stamp. See if we can create it. */
    fd = creat(cachebuf, 0777);
    if ( fd >= 0) {
	D(printf("But can create here\n"));
	close(fd);
	unlink(cachebuf);
	return 0;
    }
    D(printf("And can't create either\n"));
    /* Nope, can't create. Fill in filename in /tmp */
    tname = tempnam("/usr/tmp", "dl.");
    if ( toberemovedp >= toberemoved+NREMOVE ) {
	dl_error("Too many temporary load images created");
	return 0;
    }
    if ( toberemovedp == toberemoved )
      atexit(dl_remove_tmp);
    *toberemovedp++ = tname;
    strcpy(cachebuf, tname);
    return 0;
}

