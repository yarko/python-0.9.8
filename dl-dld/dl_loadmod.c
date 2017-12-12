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
** An emulation of Jack's dld interface on top of GNU's dld.
** This only works if the calling program is linked with -Bstatic (or gcc)!!!
*/

#include "dl.h"
#include "dld.h"

#include <stdio.h>
#include <ctype.h>
#include <nlist.h>

#define D(x)

static int inited;

dl_funcptr
dl_loadmod(thisfile, loadfile, entrypoint)
	char *thisfile, *loadfile, *entrypoint;
{
	int err;
	char *libs;
	dl_funcptr func;
	
	if (!inited) {
		err = dld_init(dl_getbinaryname(thisfile));
		if (err) {
			dld_perror("Internal error");
			dl_error("dl_loadmod: dld_init of %s failed", thisfile);
			return 0;
		}
		inited = 1;
	}

	D(fprintf(stderr, "calling dld_link(%s)\n", loadfile));
	err = dld_link(loadfile);
	if (err) {
		dld_perror("Internal error");
		dl_error("dl_loadmod: dld_link of %s failed", loadfile);
		return 0;
	}

	libs = dl_findlibs(loadfile);
	if (libs) {
		char *p, *q;
		int i;
		char buf[1024];
		D(fprintf(stderr, "libs: '%s'\n", libs));
		p = libs;
		for (;;) {
			while (*p && isspace(*p))
				p++;
			if (!*p)
				break;
			q = p;
			while (*q && !isspace(*q))
				q++;
			i = q-p;
			strncpy(buf, p, i);
			buf[i] = '\0';
			D(fprintf(stderr, "calling dld_link(%s)\n", buf));
			err = dld_link(buf);
			if (err && err != DLD_EUNDEFSYM) {
				dld_perror("Internal error");
				dl_error("dl_loadmod: dld_link of library %s failed", buf);
			}
			p = q;
		}
	}

	if (dld_undefined_sym_count) {
		int i;
		char **pp;
		pp = dld_list_undefined_sym();
		for (i = 0; i < dld_undefined_sym_count; i++) {
			fprintf(stderr, "\t%s\n", pp[i]);
		}
		free(pp);
		dl_error("dl_loadmod: %d undefined symbols remain",
			 dld_undefined_sym_count);
		return 0;
	}
	
	if (!dld_function_executable_p(entrypoint)) {
		dl_error("dl_loadmod: function %s not executable", entrypoint);
	}
	
	D(fprintf(stderr, "call dld_get_func(%s)\n", entrypoint));
	func = (dl_funcptr) dld_get_func(entrypoint);
	if (func == 0)
		dl_error("dl_loadmod: function %s not found", entrypoint);

	return func;
}

int
dl_loadmod_mult(thisfile, loadfile, nl)
	char *thisfile, *loadfile;
	struct nlist nl[];
{
	int err, i, n;
	char *libs;
	dl_funcptr func;
	
	if (!inited) {
		err = dld_init(dl_getbinaryname(thisfile));
		if (err) {
			dld_perror("Internal error");
			dl_error("dl_loadmod_mult: dld_init of %s failed",
				 thisfile);
			return 0;
		}
		inited = 1;
	}

	D(fprintf(stderr, "calling dld_link(%s)\n", loadfile));
	err = dld_link(loadfile);
	if (err) {
		dld_perror("Internal error");
		dl_error("dl_loadmod_mult: dld_link of %s failed", loadfile);
		return 0;
	}

	libs = dl_findlibs(loadfile);
	if (libs) {
		char *p, *q;
		int i;
		char buf[1024];
		D(fprintf(stderr, "libs: '%s'\n", libs));
		p = libs;
		for (;;) {
			while (*p && isspace(*p))
				p++;
			if (!*p)
				break;
			q = p;
			while (*q && !isspace(*q))
				q++;
			i = q-p;
			strncpy(buf, p, i);
			buf[i] = '\0';
			D(fprintf(stderr, "calling dld_link(%s)\n", buf));
			err = dld_link(buf);
			if (err && err != DLD_EUNDEFSYM) {
				dld_perror("Internal error");
				dl_error("dl_loadmod_mult: dld_link of library %s failed", buf);
			}
			p = q;
		}
	}

	if (dld_undefined_sym_count) {
		int i;
		char **pp;
		pp = dld_list_undefined_sym();
		for (i = 0; i < dld_undefined_sym_count; i++) {
			fprintf(stderr, "\t%s\n", pp[i]);
		}
		free(pp);
		dl_error("dl_loadmod_mult: %d undefined symbols remain",
			 dld_undefined_sym_count);
		return 0;
	}
	
	for (i = n = 0; nl[i].n_name != 0; i++) {
		if (!dld_function_executable_p(nl[i].n_name)) {
			nl[i].n_value = 0;
			nl[i].n_type = 0;
			continue;
		}
		
		D(fprintf(stderr, "call dld_get_func(%s)\n", nl[i].n_name));
		nl[i].n_value = (unsigned long) dld_get_func(nl[i].n_name);
		nl[i].n_type = 1;
		n += (nl[i].n_value != 0);
	}
	return n;
}
