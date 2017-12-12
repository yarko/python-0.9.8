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

/* JPEG module */

#include "allobjects.h"

#include "modsupport.h"

#include "sigtype.h"

char * jpcompress PROTO((char *, int, int, int, char **, int *));
char * jpdecompress PROTO((char *, int, int *, int *, int *, char **));
char * jpsetoption PROTO((char *, int));

static object * JpegError;

#define NOCOPY

#ifdef NOCOPY
/*
** We replace malloc/realloc (as used in the jpeg package)
** by our own version, which allocates strings immedeately.
** This way we can skip the final copy.
*/
static object *ourstring;
static char *ourcharp;

static char *
ourmalloc(size)
    int size;
{
    ourstring = newsizedstringobject(NULL, size);
    if ( ourstring == NULL )
	return NULL;
    ourcharp = getstringvalue(ourstring);
    return ourcharp;
}

static char *
ourrealloc(ptr, size)
    char *ptr;
    int size;
{
    if ( ptr != ourcharp )
	fatal("jpeg ourrealloc: wrong pointer");
    if ( resizestring(&ourstring, size) < 0 )
	return NULL;
    ourcharp = getstringvalue(ourstring);
    return ourcharp;
}

#if 0
static void
ourfree(ptr)
    char *ptr;
{
    if ( ptr != ourcharp )
	fatal("jpeg ourfree: wrong pointer");
    DECREF(ourstring);
}
#endif

static object *
ourgetobject(ptr,size)
    char *ptr;
{
    if ( ptr != ourcharp )
	fatal("jpeg ourgetobject: wrong pointer");
    return ourstring;
}

#define ourfreecopiedptr(ptr)

extern char *(*jp_mallocoutbuf)();
extern char *(*jp_reallocoutbuf)();
#else
#define ourgetobject(ptr,size) newsizedstringobject(ptr,size)
#define ourfreecopiedptr(ptr) free(ptr)
#endif /* NOCOPY */

static object *
jpeg_compress(self, args)
	object *self;
	object *args;
{
	char *data, *rv, *errmsg;
	int w, h, bytes=4, size;
	object *objret;

	if (!getargs(args, "(s#ii)", &data, &size, &w, &h)) {
		err_clear();
		if (!getargs(args, "(s#iii)", &data, &size, &w, &h, &bytes))
			return NULL;
		if (bytes != 1 && bytes != 4) {
			err_setstr(JpegError,
				   "Can only handle 1 or 4 byte pictures");
			return NULL;
		}
	}
	if (size != w*h*bytes) {
		err_setstr(JpegError, "Incorrect data length");
		return NULL;
	}
	errmsg = jpcompress(data,w,h,bytes,&rv,&size);
	if ( errmsg ) {		/*XXXX This is wrong */
	    err_setstr(JpegError,errmsg);
	    return NULL;
	}
	if( objret = ourgetobject(rv,size)) {
	    ourfreecopiedptr(rv);
	    return objret;
	} else {
	    ourfreecopiedptr(rv);
	    return NULL;
	}
}

static object *
jpeg_decompress(self, args)
	object *self;
	object *args;
{
	char *rv, *errmsg, *data;
	int w, h, size, bytes;
	object *v, *result;

	if (!getargs(args, "s#", &data, &size))
	    return NULL;
	errmsg = jpdecompress(data,size,&w,&h,&bytes,&rv);
	if ( errmsg ) {		/*XXXX Wrong */
	    err_setstr(JpegError,errmsg);
	    return NULL;
	}
	v = ourgetobject(rv,w*h*bytes);
	result = mkvalue("Oiii", v, w, h, bytes);
	DECREF(v);
	return result;
}

static object *
jpeg_setoption(self, args)
	object *self;
	object *args;
{
	char *opname;
	int opvalue;
	char *errstr;

	if (!getargs(args, "(si)", &opname, &opvalue))
		return NULL;
	errstr = jpsetoption(opname, opvalue);
	if ( errstr ) {
	    err_setstr(JpegError, errstr);
	    return NULL;
	}
	INCREF(None);
	return None;
}

static struct methodlist jpeg_methods[] = {
	{"compress",	jpeg_compress},
	{"decompress",	jpeg_decompress},
	{"setoption",	jpeg_setoption},
	{NULL,		NULL}		/* sentinel */
};


void
initjpeg()
{
	object *m, *d;
	m = initmodule("jpeg", jpeg_methods);
	d = getmoduledict(m);
	JpegError = newstringobject("jpeg.error");
	if ( JpegError == NULL || dictinsert(d,"error",JpegError) )
	    fatal("can't define jpeg.error");
	jp_mallocoutbuf = ourmalloc;
	jp_reallocoutbuf = ourrealloc;
}
