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

/* Scanner module -- helps in constructing efficient scanners */

#include "allobjects.h"
#include "modsupport.h"
#include "ceval.h"
#include "regexpr.h"

static object *
scanner_scan(self, args)
	object *self;
	object *args;
{
	object *input; /* File object */
	char *wsp; /* String of characters */
	int wsplen;
	char *token; /* Regular expression */
	int tokenlen;
	object *handler; /* Function */
	struct re_pattern_buffer patbuf; /* Compiled regex */
	char fastmap[256]; /* Storage for regex' "fastmap" */
	char *error; /* Compilation error */
	object *result; /* Final result */

	/* Extract the arguments */
	if (!getargs(args, "(Os#s#O)",
		     &input, &wsp, &wsplen, &token, &tokenlen, &handler))
		return NULL;

	/* Compile the regular expression */
	patbuf.buffer = NULL;
	patbuf.allocated = 0;
	patbuf.fastmap = fastmap;
	patbuf.translate = NULL;
	error = re_compile_pattern(token, tokenlen, &patbuf);
	if (error != NULL) {
		err_setstr(RuntimeError, error);
		XDEL(patbuf.buffer);
		return NULL;
	}

	/* Read and scan input lines until handler() returns not None */
	result = NULL;
	while (result == NULL && !err_occurred()) {
		object *line = filegetline(input, 0);
		char *buf; /* line as C string */
		int buflen;
		int bufpos;
		if (line == NULL)
			break;
		if (!is_stringobject(line)) {
			err_setstr(TypeError, "readline didn't return string");
			DECREF(line);
			break;
		}
		buf = getstringvalue(line);
		buflen = getstringsize(line);
		if (buflen == 0) {
			err_setstr(EOFError, "scanner encounters EOF");
			DECREF(line);
			break;
		}

		/* Walk through the line, skip whitespace, handle tokens */
		bufpos = 0;
		while (bufpos < buflen) {
			char c = buf[bufpos];
			char *p = wsp;
			int i = wsplen;
			object *x, *y;
			/* Is it a space character? */
			while (--i >= 0) {
				if (c == *p++) {
					bufpos++;
					goto nextc; /* Yes -- skip it */
				}
			}
			i = re_match(&patbuf, buf, buflen, bufpos,
				     (struct re_registers *)NULL);
			if (i <= 0) {
				if (i < -1) {
					err_setstr(RuntimeError,
						   "re_match failed");
					break;
				}
				/* Bad char or empty token -- handle 1 char */
				i = 1;
			}
			x = mkvalue("(s#)", buf + bufpos, i);
			if (x == NULL)
				break;
			y = call_object(handler, x);
			DECREF(x);
			if (y != None) {
				result = y;
				break;
			}
			DECREF(y);
			bufpos += i;
		nextc:	;
		}

		DECREF(line);
	}

	XDEL(patbuf.buffer);
	return result;
}

static struct methodlist scanner_methods[] = {
	{"scan",	scanner_scan},
	{NULL,		NULL}		/* sentinel */
};


void
initscanner()
{
	initmodule("scanner", scanner_methods);
}
