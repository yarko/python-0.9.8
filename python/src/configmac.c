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

/* Configuration for the Mac (THINK_C or MPW) */

#include <stdio.h>

#include "patchlevel.h"

#define VERSION "0.9.%d (%s)"

#define DATE __DATE__

/* Assume we always use STDWIN; remove this line if you really don't want it */
#define USE_STDWIN

#ifdef USE_STDWIN
#include "stdwin.h"
#endif

char version[80];

void
initargs(p_argc, p_argv)
	int *p_argc;
	char ***p_argv;
{
	sprintf(version, VERSION, PATCHLEVEL, DATE);
#ifdef USE_STDWIN
#ifdef THINK_C_3_0
	wsetstdio(1);
#endif
	wargs(p_argc, p_argv);
#endif /* USE_STDWIN */
	if (*p_argc < 2) {
		printf("Python %s.\n", version);
		printf(
"Copyright 1990, 1991, 1992 Stichting Mathematisch Centrum, Amsterdam\n");
	}
}

void
initcalls()
{
}

void
donecalls()
{
#ifdef USE_STDWIN
	wdone();
#endif
}

#ifndef PYTHONPATH
/* On the Mac, the search path is a space-separated list of directories */
#define PYTHONPATH ": :lib :demo"
#endif

char *
getpythonpath()
{
	return PYTHONPATH;
}


/* Table of built-in modules.
   These are initialized when first imported. */

/* Standard modules */
extern void inittime();
extern void initmath();
extern void initregex();
	
/* Mac-specific modules */
extern void initmac();
#ifdef USE_STDWIN
extern void initstdwin();
#endif
extern void initmarshal();

struct {
	char *name;
	void (*initfunc)();
} inittab[] = {
	/* Standard modules */
	{"time",	inittime},
	{"math",	initmath},
	{"regex",	initregex},
	
	/* Mac-specific modules */
	{"mac",		initmac},
#ifdef USE_STDWIN
	{"stdwin",	initstdwin},
#endif
	{"marshal",	initmarshal},
	{0,		0}		/* Sentinel */
};
