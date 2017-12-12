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
** dload1 - Dynamically load a file.
*/

#define _auxtemp _auxtemp3	/* Bug in ldfcn.h */

#include <stdio.h>
#include <filehdr.h>
#include <syms.h>
#include <ar.h>
#include <ldfcn.h>
#include <aouthdr.h>

#include "dl.h"

#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif /* DEBUG */

/*
** dl_ldfile - Load an incremental file.
** dl_ldfile determines wether to load a ZMAGIC file or something else
** and calls the appropriate routine to load it.
*/
dl_ldfile(fn)
    char *fn;
{
    LDFILE *ldptr;
    int rv;
    AOUTHDR aouth;

    ldptr = ldopen(fn, NULL);
    if ( ldptr == 0 ) {
	dl_error(0, fn);
	return 0;
    }
    /*
    ** Unfortunately, the mld library doesn't provide us with the magic
    ** number.
    */
    if ( ldohseek(ldptr) == FAILURE ) {
	dl_error("Ill-formatted binary %s (cannot seek to header)", fn);
	ldclose(ldptr);
	return 0;
    }
    if (  FREAD((char *)&aouth, 1, sizeof(aouth), ldptr) != sizeof(aouth)) {
	dl_error("Ill-formatted binary %s (cannot read)", fn);
	D(printf("File-pos=%d\n", FTELL(ldptr)));
	ldclose(ldptr);
	return 0;
    }
    if ( aouth.magic == NMAGIC )
      rv = dl_ldnfilep(ldptr);
    else if( aouth.magic == ZMAGIC )
#if 0
      if ( getenv("DLDEBUG") == 0 )
	  rv = dl_ldnfilep(ldptr);     /* XXXX should be z */
      else
#endif
	  rv = dl_ldzfilep(ldptr, fn);
    else {
	dl_error("Not ZMAGIC or NMAGIC file: %s", fn);
	rv = 0;
    }
    ldclose(ldptr);
    return rv;
}
    
