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
** dl_getbinaryname - Convert program name to full pathname.
*/
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "dl.h"

#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif

/* Default path from sh(1) in Irix 4.0.1 */
#define DEF_PATH ":/usr/sbin:/usr/bsd:/bin:/usr/bin:/usr/bin/X11"

char *
dl_getbinaryname(argv0)
    char *argv0;
{
	char *p, *q;
	char *path;
	static char buf[1028];
	int i;
	struct stat st;
	char *getenv();

	if (strchr(argv0, '/') != NULL) {
		D(printf("binary includes slash: %s\n", argv0));
		return argv0;
	}
	path = getenv("PATH");
	if (path == NULL)
		path = DEF_PATH;
	p = q = path;
	for (;;) {
		while (*q && *q != ':')
			q++;
		i = q-p;
		strncpy(buf, p, i);
		if (q > p && q[-1] != '/')
			buf[i++] = '/';
		strcpy(buf+i, argv0);
		if (stat(buf, &st) >= 0) {
			if (S_ISREG(st.st_mode) &&
			    (st.st_mode & 0111)) {
				D(printf("found binary: %s\n", buf));
				return buf;
			}
		}
		if (!*q)
			break;
		p = ++q;
	}
	D(printf("can't find binary: %s\n", argv0));
	return argv0;
}
