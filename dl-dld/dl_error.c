/***********************************************************
Copyright 1991, 1992 by Stichting Mathematisch Centrum, Amsterdam, The
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
** dl_error - dl error handling.
*/

#include "dl.h"
#include <stdio.h>

dl_errortype *dl_ehptr = dl_defaulterror;
dl_errortype *dl_mhptr = dl_defaultmessage;

void
dl_seterror(eh)
    dl_errortype *eh;
{
    if ( eh == 0 )
      dl_ehptr = dl_defaulterror;
    else
      dl_ehptr = eh;
}

void
dl_defaulterror(str)
    char *str;
{
    fprintf(stderr, "%s\n", str);
}

void
dl_error(fmt, arg)
    char *fmt;
    int arg;
{
    char errbuf[512];
    extern int errno;

    if ( fmt ) {
	sprintf(errbuf, fmt, arg);
    } else {
	sprintf(errbuf, "libdl: %s: %s", arg, strerror(errno));
    }
    (*dl_ehptr)(errbuf);
}

void
dl_setmessage(eh)
    dl_errortype *eh;
{
    if ( eh == 0 )
      dl_ehptr = dl_defaultmessage;
    else
      dl_ehptr = eh;
}

void
dl_defaultmessage(str)
    char *str;
{
    fprintf(stderr, "%s\n", str);
}

void
dl_message(fmt, arg)
    char *fmt;
    int arg;
{
    char msgbuf[512];

    sprintf(msgbuf, fmt, arg);
    (*dl_mhptr)(msgbuf);
}

void
dl_nomessage(str)
    char *str;
{
}
