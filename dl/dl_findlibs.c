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
** dl_findlibs - Find optional ld libraries for module.
*/
#include "dl.h"

static char flbuf[1030];

char *
dl_findlibs(obj)
    char *obj;
{
    int fd, n;
    
    strncpy(flbuf, obj, 1024);
    flbuf[1024] = 0;
    if ( strncmp(flbuf+strlen(flbuf)-2, ".o", 2) == 0)
      flbuf[strlen(flbuf)-2] = 0;
    strcat(flbuf, ".libs");
    if ((fd=open(flbuf, 0)) < 0 ) {
	flbuf[0] = 0;
	return flbuf;
    }
    n = read(fd, flbuf, 1024);
    close(fd);
    if ( n < 0 || n == 1024 )
      return 0;
    n--;
    if ( flbuf[n] = '\n' )
      n--;
    flbuf[n+1] = 0;
    return flbuf;
}
    
