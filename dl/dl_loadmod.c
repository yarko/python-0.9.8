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
** dl_loadmod - Load module and return address.
*/

#include <nlist.h>
#include <stdio.h>
#include <string.h>

#include "dl.h"
#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif

/*
** The following variable is a guess for the upper bound on text- and
** data-segment size. Bigger dynamically loaded segments will very
** sporadically cause the program to crash (with an error message, though).
*/
long segsizeguess = 1024*1024;

char incr_name[512];

dl_funcptr
dl_loadmod(binary, module, rtn)
    char *binary, *module, *rtn;
{
    int rv;
    struct nlist nl[2];
    char *ldname;

    if ( dl_loadmod_only(binary, module, &ldname) == 0 )
      return 0;
    bzero((char *)nl, sizeof(nl));
    nl[0].n_name = rtn;
    rv = nlist(ldname, nl);
    if ( rv < 0 ) {
	dl_error("No valid name list in %s", ldname);
	return 0;
    }
    if ( nl[0].n_type == 0) {
	dl_error("No such symbol in binary: %s", rtn);
	return 0;
    }
    return (dl_funcptr)nl[0].n_value;
}

int
dl_loadmod_mult(binary, module, nl)
    char *binary, *module;
    struct nlist *nl;
{
    int i, n, rv;
    char *ldname;
    
    if ( dl_loadmod_only(binary, module, &ldname) == 0 )
      return 0;
    rv = nlist(ldname, nl);
    if ( rv < 0 ) {
	dl_error("No valid name list in %s", ldname);
	return 0;
    }
    n = 0;
    for (i=0; nl[i].n_name; i++) {
	if ( nl[0].n_type ) n++;
    }
    return n;
}
int
dl_loadmod_only(binary, module, ldnamep)
    char *binary, *module, **ldnamep;
{
    int mtime, mtime2;
    char *ldname;
    char *libs;
    unsigned long taddr, daddr;
    extern end, etext;
    long texttop, datatop;
    int is_incr = 0;

    if ( binary == NULL ) {
	/* No name specified. Incremental load */
	if ( incr_name[0] == '\0' ) {
	    dl_error("Incremental load requested, but no file name", 0);
	    return 0;
	}
	binary = incr_name;
	is_incr = 1;
    }
    /*
    ** Compute expected version stamp on loadimage
    */
    binary = dl_getbinaryname(binary);
    binary = dl_expand_script_binary(binary);
    if ( (mtime=dl_gettime(binary)) <= 0) {
	dl_error(0, binary); 
	return 0;
    }
    if ( (mtime2=dl_gettime(module)) <= 0) {
	dl_error(0, module);
	return 0;
    }
    mtime = (mtime+mtime2) & 0xffff;
    /*
    ** Go hunt for binary.
    */
    D(printf("dl_loadmod: mtime=%x\n", mtime));
    if ( dl_findcache(module, mtime, &ldname) == 0) {
	/* Doesn't exist, or out of date. Create it. */
	D(printf("dl_loadmod: not cached\n"));
	libs = dl_findlibs(module);
	D(printf("dl_loadmod: libs=%s\n", libs));
	if ( !dl_hashaddrs(module, segsizeguess, segsizeguess,
			   &texttop, &datatop) ) {
	    dl_error("dl_loadmod: no memory space for module", 0);
	    return 0;
	}
	if ( !dl_linkfile(ldname, binary, module, libs, texttop,
			  datatop, mtime) )
	  return 0;
	/* XXXX Should check here that the newly-linked module actually fits */
    }
    if ( is_incr ) {
	D(printf("dl_loadmod: zapping _end, _etext and _edata\n"));
	dl_remsym(ldname, "_end");
	dl_remsym(ldname, "_etext");
	dl_remsym(ldname, "_edata");
    }
    D(printf("dl_loadmod: cache ok, loading %s\n", ldname));
    if( dl_ldfile(ldname) == 0)
      return 0;
    *ldnamep = ldname;
    strncpy(incr_name, ldname, 511);
    return 1;
}

void
dl_setincr(name)
    char *name;
{
    name = dl_expand_script_binary(name);
    strncpy(incr_name, name, 511);
}

char *
dl_expand_script_binary(name)
    char *name;
{
    FILE *fp;
    static char buf[512];
    char *bp;
    char *endp;

    if ( name == 0 )
      return name;
    if ( (fp=fopen(name, "r")) == NULL ) {
	/* Cannot open file, so just use given name */
	return name;
    }
    if ( fgets(buf, 511, fp) == NULL ) {
	fclose(fp);
	return name;
    }
    fclose(fp);

    if ( buf[0] != '#' || buf[1] != '!' )
      return name;
    /* For scripts, locate the real filename. */
    buf[strlen(buf)-1] = '\0';
    bp = buf + 2;		/* Find beginning */
    while ( *bp == ' ' )
      bp++;
    endp = strchr(bp, ' ');	/* And end. */
    if ( endp ) *endp = '\0';
    D(printf("dl_expand_script_binary: binary in %s\n", bp));
    return bp;
}

dl_setsegsizeguess(size)
    long size;
{
    if ( size > segsizeguess )
      segsizeguess = size;
}
