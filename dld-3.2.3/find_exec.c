/* Given a filename, dld_find_executable searches the directories listed in the
   environment variable PATH for a file with that filename.
   A new copy of the complete path name of that file is returned.  This new
   string may be disposed by free() later on.
*/

/* This file is part of DLD, a dynamic link/unlink editor for C.
   
   Copyright (C) 1990 by W. Wilson Ho.

   The author can be reached electronically by how@cs.ucdavis.edu or
   through physical mail at:

   W. Wilson Ho
   Division of Computer Science
   University of California at Davis
   Davis, CA 95616
 */

/* This program is free software; you can redistribute it and/or modify it
   under the terms of the GNU General Public License as published by the
   Free Software Foundation; either version 1, or (at your option) any
   later version. */

#include <sys/file.h>
#include <sys/param.h>
#include <strings.h>

#define DEFAULT_PATH ".:~/bin::/usr/local/bin:/usr/new:/usr/ucb:/usr/bin:/bin:/usr/hosts"

static char *
copy_of (s)
register char *s;
{
    register char *p = (char *) malloc (strlen(s)+1);

    if (!p) return 0;

    *p = 0;
    strcpy (p, s);
    return p;
}

/* ABSOLUTE_FILENAME_P (fname): True if fname is an absolute filename */
#ifdef atarist
#define ABSOLUTE_FILENAME_P(fname)	((fname[0] == '/') || \
	(fname[0] && (fname[1] == ':')))
#else
#define ABSOLUTE_FILENAME_P(fname)	(fname[0] == '/')
#endif /* atarist */

char *
dld_find_executable (file)
char *file;
{
    char *search;
    register char *p;
    
    if (ABSOLUTE_FILENAME_P(file))
	return copy_of (file);
    
    if (((search = (char *) getenv("DLDPATH")) == 0) &&
	((search = (char *) getenv("PATH")) == 0))
	search = DEFAULT_PATH;
	
    p = search;
    
    while (*p) {
	char  name[MAXPATHLEN];
	register char *next;

	next = name;
	
	/* copy directory name into [name] */
	while (*p && *p != ':') *next++ = *p++;
	*next = 0;
	if (*p) p++;

	if (name[0] == '.' && name[1] == 0)
	    getwd (name);
	
	strcat (name, "/");
	strcat (name, file);
	      
	if (access (name, X_OK) == 0)
	    return copy_of (name);
    }

    return 0;
}
