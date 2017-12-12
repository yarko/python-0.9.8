/***********************************************************
Copyright 1991, 1992, 1993 by Stichting Mathematisch Centrum,
Amsterdam, The Netherlands.

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

/* Configurable Python configuration file */

/* These modules are normally always included, but *may* be taken out */
#define USE_GRP		1	/* Use together with pwd */
#define USE_MARSHAL	1	/* This is linked anyway */
#define USE_MATH	1
#define USE_PWD		1	/* Use together with grp */
#define USE_POSIX	1
#define USE_SELECT	1
#define USE_SOCKET	1
#define USE_STRUCT	1
#define USE_TIME	1

#include "PROTO.h"
#include "mymalloc.h"

#include "patchlevel.h"

#define VERSION "0.9.%d (%s)"

#ifdef __DATE__
#define DATE __DATE__
#else
#define DATE ">= 8 Jan 1993"
#endif

#include <stdio.h>

#ifdef USE_STDWIN
#include <stdwin.h>
#endif

char version[80];

char *argv0;

/*ARGSUSED*/
void
initargs(p_argc, p_argv)
	int *p_argc;
	char ***p_argv;
{
	sprintf(version, VERSION, PATCHLEVEL, DATE);

	argv0 = **p_argv;

#ifdef USE_STDWIN
	wargs(p_argc, p_argv);
#endif
	if (*p_argc < 2 && isatty(0) && isatty(1))
	{
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
#ifdef USE_AUDIO
	asa_done();
#endif
}

#ifndef PYTHONPATH
#define PYTHONPATH ".:/usr/local/lib/python"
#endif

extern char *getenv();

char *
getpythonpath()
{
	char *path = getenv("PYTHONPATH");
	char *defpath = PYTHONPATH;
	char *buf;
	int n;

	if (path == 0 || *path == '\0')
		return defpath;
	n = strlen(path) + strlen(defpath) + 2;
	buf = malloc(n);
	if (buf == NULL)
		return path; /* XXX too bad -- but not likely */
	strcpy(buf, path);
	strcat(buf, ":");
	strcat(buf, defpath);
	return buf;
}


/* Table of built-in modules.
   These are initialized when first imported. */

/* Standard modules */

#ifdef USE_AL
extern void inital();
#endif
#ifdef USE_AMOEBA
extern void initamoeba();
#endif
#ifdef USE_AUDIO
extern void initaudio();
#endif
#ifdef USE_AUDIOOP
extern void initaudioop();
#endif
#ifdef USE_CD
extern void initcd();
#endif
#ifdef USE_DBM
extern void initdbm();
#endif
#ifdef USE_FCNTL
extern void initfcntl();
#endif
#ifdef USE_FL
extern void initfl();
#endif
#ifdef USE_FM
extern void initfm();
#endif
#ifdef USE_GL
extern void initgl();
#endif
#ifdef USE_GRP
extern void initgrp();
#endif
#ifdef USE_IMGFILE
extern void initimgfile();
#endif
#ifdef USE_JPEG
extern void initjpeg();
#endif
#ifdef USE_MARSHAL
extern void initmarshal();
#endif
#ifdef USE_MATH
extern void initmath();
#endif
#ifdef USE_NIS
extern void initnis();
#endif
#ifdef USE_PANEL
extern void initpanel();
#endif
#ifdef USE_POSIX
extern void initposix();
#endif
#ifdef USE_PWD
extern void initpwd();
#endif
#ifdef USE_REGEX
extern void initregex();
#endif
#ifdef USE_ROTOR
extern void initrotor();
#endif
#ifdef USE_SELECT
extern void initselect();
#endif
#ifdef USE_SGI
extern void initsgi();
#endif
#ifdef USE_SOCKET
extern void initsocket();
#endif
#ifdef USE_STDWIN
extern void initstdwin();
#endif
#ifdef USE_STROP
extern void initstrop();
#endif
#ifdef USE_STRUCT
extern void initstruct();
#endif
#ifdef USE_SUNAUDIODEV
extern void initsunaudiodev();
#endif
#ifdef USE_THREAD
extern void initthread();
#endif
#ifdef USE_SV
extern void initsv();
#endif
#ifdef USE_CL
extern void initcl();
#endif
#ifdef USE_TIME
extern void inittime();
#endif
#ifdef USE_IMAGEOP
extern void initimageop();
#endif
#ifdef USE_MPZ
extern void initmpz();
#endif
#ifdef USE_MD5
extern void initmd5();
#endif
/* -- ADDMODULE MARKER 1 -- */

struct {
	char *name;
	void (*initfunc)();
} inittab[] = {

#ifdef USE_AL
	{"al",		inital},
#endif

#ifdef USE_AMOEBA
	{"amoeba",	initamoeba},
#endif

#ifdef USE_AUDIO
	{"audio",	initaudio},
#endif

#ifdef USE_AUDIOOP
	{"audioop",	initaudioop},
#endif

#ifdef USE_CD
	{"cd",		initcd},
#endif

#ifdef USE_DBM
	{"dbm",		initdbm},
#endif

#ifdef USE_FCNTL
	{"fcntl",	initfcntl},
#endif

#ifdef USE_FL
	{"fl",		initfl},
#endif

#ifdef USE_FM
	{"fm",		initfm},
#endif

#ifdef USE_GL
	{"gl",		initgl},
#endif

#ifdef USE_GRP
	{"grp",		initgrp},
#endif

#ifdef USE_IMGFILE
	{"imgfile",	initimgfile},
#endif

#ifdef USE_JPEG
	{"jpeg",	initjpeg},
#endif

#ifdef USE_MARSHAL
	{"marshal",	initmarshal},
#endif

#ifdef USE_MATH
	{"math",	initmath},
#endif

#ifdef USE_NIS
	{"nis",		initnis},
#endif

#ifdef USE_PANEL
	{"pnl",		initpanel},
#endif

#ifdef USE_POSIX
	{"posix",	initposix},
#endif

#ifdef USE_PWD
	{"pwd",		initpwd},
#endif

#ifdef USE_REGEX
	{"regex",	initregex},
#endif

#ifdef USE_ROTOR
	{"rotor",	initrotor},
#endif

#ifdef USE_SELECT
	{"select",	initselect},
#endif

#ifdef USE_SGI
	{"sgi",		initsgi},
#endif

#ifdef USE_SOCKET
	{"socket",	initsocket},
#endif

#ifdef USE_STDWIN
	{"stdwin",	initstdwin},
#endif

#ifdef USE_STROP
	{"strop",	initstrop},
#endif

#ifdef USE_STRUCT
	{"struct",	initstruct},
#endif

#ifdef USE_SUNAUDIODEV
	{"sunaudiodev",	initsunaudiodev},
#endif

#ifdef USE_SV
	{"sv",		initsv},
#endif

#ifdef USE_CL
	{"cl",		initcl},
#endif

#ifdef USE_THREAD
	{"thread",	initthread},
#endif

#ifdef USE_TIME
	{"time",	inittime},
#endif

#ifdef USE_IMAGEOP
       {"imageop", initimageop},
#endif

#ifdef USE_MPZ
       {"mpz", initmpz},
#endif

#ifdef USE_MD5
       {"md5", initmd5},
#endif

/* -- ADDMODULE MARKER 2 -- */

	{0,		0}		/* Sentinel */
};
