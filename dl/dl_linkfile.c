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
** dl_linkfile - Link a file.
*/

dl_linkfile(ofile, mfile, ifile, libs, taddr, daddr, vstamp)
    char *ofile, *mfile, *ifile, *libs;
    unsigned long taddr, daddr;
    int vstamp;
{
    char namebuf[512];
    char cmdbuf[512];
    int rv;

    sprintf(namebuf, "%s.%d", ofile, getpid());
    sprintf(cmdbuf,
	    "ld -o %s -x -A %s -allow_jump_at_eop -z -T %x -D %x -VS %d %s %s",
	    namebuf, mfile, taddr, daddr, vstamp, ifile, libs);
    dl_message("dl: running linker on module %s:", ifile);
    rv = system(cmdbuf);
    dl_message("dl: link done");
    if ( rv == 0 ) {
	unlink(ofile);
	if ( link(namebuf, ofile) < 0 ) {
	    dl_error(0, ofile);
	    return 0;
	}
	unlink(namebuf);
    }
    return rv == 0;
}
