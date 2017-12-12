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
** Definitions of dl library modules.
*/

#ifdef __STDC__
#define _PROTO(x) x
#else
#define _PROTO(x) ()
#endif

typedef void dl_errortype _PROTO((char *));
typedef void (*dl_funcptr) _PROTO((void));

dl_funcptr dl_loadmod _PROTO((char *, char *, char *));
void dl_error(); /* _PROTO((char *, int)); /* XXX Should use varargs/starg */
void dl_message(); /* _PROTO((char *, int)); /* XXX Should use varargs/starg */
extern dl_errortype dl_defaulterror; /* These are functions! */
extern dl_errortype dl_defaultmessage;
extern dl_errortype dl_nomessage;
void dl_setmessage _PROTO((dl_errortype *));
void dl_seterror _PROTO((dl_errortype *));

/* Internal */
char *dl_findlibs _PROTO((char *));
char *dl_getbinaryname _PROTO((char *));

#undef _PROTO
