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
** dl_ldzfilep - Load ZMAGIC file using mmap
*/

#define _auxtemp _auxtemp1	/* A bug in ldfcn.h */

#include <stdio.h>
#include <filehdr.h>
#include <syms.h>
#include <ar.h>
#include <ldfcn.h>
#include <scnhdr.h>
#include <nlist.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/fcntl.h>
#include <sys/mman.h>

#include "dl.h"

#ifdef DEBUG
#define D(x) (x)
#else
#define D(x)
#endif /* DEBUG */

/*
** dl_ldzfilep loads a ZMAGIC file into memory using mmap() calls (thereby
** making at least the text segment of the binary demand-paged form the
** original load image).
**
** Due to some ideosyncracies in the way mmap() work we have to collect all
** BSS and DATA segments and map them together. The current code only works
** well if the following two things are true:
** - All data segments (rdata, data, sdata, etc) are contiguous, and the
**   sections in the load file are sorted on address and their data is
**   stored contiguous
** - All bss segment section descriptors are contiguous, their sections are
**   sorted on address and they follow all the data segments.
**
** As far as I can tell this is true for all normal binaries.
** Unexpected things may happen if this is untrue, since the routine does
** only some very cursory checks to verify these hypotheses.
*/
dl_ldzfilep(ldptr, fn)
    LDFILE *ldptr;
    char *fn;
{
    int i;
    int nsect;				/* Number of sections */
    struct scnhdr shdr;			/* Current section header */
    int fd;				/* load file fd (for mmap) */
    int nullfd;				/* /dev/zero fd (for bss mmap) */
    unsigned long addr, eaddr, off;	/* rounded section address/file-off */
    unsigned long pagesize, pagemask;	/* mmu parameters */
    void *rv;				/* mmap return value */
    long size;				/* new bss size */
    unsigned long lodata, hidata, lobss, hibss;	/* Data/bss location */
    unsigned long offdata;
    int hasdata, hasbss;

    /*
    ** First some initializations.
    */
    pagesize = getpagesize();
    pagemask = pagesize-1;
    assert ( (pagesize|pagemask) == pagesize+pagemask);
    fd = open(fn,O_RDONLY);
    if(fd < 0) {
	dl_error("Could not open fd for mmap on %s",fn);
	return 0;
    }
    if ( (nullfd = open("/dev/zero", 0)) < 0) {
	dl_error(0, "/dev/zero");
	close(fd);
        return 0;
    }
    nsect = HEADER(ldptr).f_nscns;
    D(printf("loadfile: %d sections\n", nsect));
    D(printf("loadfile: version stamp=%d, 0x%x\n", SYMHEADER(ldptr).vstamp,
	     SYMHEADER(ldptr).vstamp));
    /*
    ** Now loop over the sections, and load them if needed.
    */
    lodata = lobss = 0xffffffff;
    hidata = hibss = 0;
    hasdata = hasbss = 0;
    offdata = 0xffffffff;
    for ( i=1; i<nsect+1; i++ ) {
	if ( ldshread(ldptr, i, &shdr) == FAILURE ) {
	    dl_error("Cannot read section header %d", i);
		close(nullfd); close(fd);
	    return 0;
	}
	D(printf("loadfile: section %d=%s, 0x%x:0x%x@0x%x type 0x%x\n", i,
	       shdr.s_name, shdr.s_vaddr, shdr.s_size, shdr.s_scnptr, shdr.s_flags));
	if(  shdr.s_flags & STYP_COMMENT ) {
	    D(printf("Skipping comment section %x\n", shdr.s_flags));
	    continue;
	}
	if ( shdr.s_scnptr &&
	                (shdr.s_vaddr&pagemask) != (shdr.s_scnptr&pagemask) ) {
	    /* Incorrectly aligned segment */
	    dl_error("Incorrect alignment in section %d", i);
		close(nullfd); close(fd);
	    return 0;
	}
	addr = shdr.s_vaddr & ~pagemask;
	eaddr = shdr.s_vaddr + shdr.s_size;
	off = shdr.s_scnptr & ~pagemask;
	D(printf("Addr %x, off %x\n", addr, off));
	/*
	** We would like to use the lower 4 bits in s_flags here to decide
	** what to do with the segment (allocate/load), but they don't seem
	** to be set correctly. So, we have to fiddle.
	*/
	switch(shdr.s_flags) {
	case STYP_TEXT:
	    if ( !dl_setrange(addr, eaddr) ) {
		dl_error("Segment does not fit. Try calling dl_setsegsizeguess(0x%x)", eaddr-addr);
		return 0;
	    }
	    rv = mmap((void *)addr, eaddr - addr, PROT_READ|PROT_EXECUTE,
			MAP_SHARED|MAP_FIXED, fd, off);
	    D(printf("rv=%x addr=%x\n", rv, addr));
	    if ( addr != (unsigned long)rv ) {
		dl_error(0, "mmap(.text)");
		close(nullfd); close(fd);
	        return 0;
	    }
	    break;
	case STYP_DATA:
	case STYP_RDATA:
	case STYP_SDATA:
	case STYP_LIT8:
	case STYP_LIT4:
	    /* Could do many more sanity checks here */
	    if ( addr < lodata) {
		if ( lodata != 0xffffffff ) {
		    dl_error("Data segments incorrectly ordered", 0);
		    close(nullfd); close(fd);
		    return 0;
		}
		lodata = addr;
	    }
	    if ( eaddr > hidata )
	      hidata = eaddr;
	    if ( off < offdata )
	      offdata = off;
	    hasdata = 1;
	    break;
	case STYP_BSS:
	case STYP_SBSS:
	    if ( addr < lobss )
	      lobss = addr;
	    if ( eaddr > hibss )
	      hibss = eaddr;
	    hasbss = 1;
	    break;
	case _STYP_RESOURCE:
	    break;
	default:
	    dl_error("Unknown section type 0x%x", shdr.s_flags);
	    close(nullfd); close(fd);
	    return 0;
	}
    }
    /*
    ** Now map in all of data space, if there is any.
    ** It seems we can't map bss space into the same region, so
    ** we map all of it private, and read it in ourselves.
    */
    if ( hasdata || hasbss ) {
	if ( hasdata && hasbss && hibss < hidata ) {
	    /* Segments in the wrong order */
	    dl_error(0, "data/bss segments in wrong order");
	    return 0;
	}
	if ( !hasdata )
	  lodata = hidata = lobss;
	if ( !hasbss )
	  lobss = hibss = hidata;
	D(printf("Data mmap(0x%x, 0x%x, ...)\n", lodata, hibss-lodata));
	if( !dl_setrange(lodata, hibss) ) {
	    dl_error("Segment does not fit. Try calling dl_setsegsizeguess(0x%x)", hibss-lodata);
	    return 0;
	}
	rv = mmap((void *)lodata, hibss-lodata, PROT_READ|PROT_WRITE,
		  MAP_PRIVATE|MAP_FIXED, nullfd, 0);
	if ( (unsigned long)rv != lodata ) {
	    D(printf("mmap(data)=0x%x, not 0x%x\n", rv, lodata));
	    dl_error(0, "mmap(data segments)");
	    close(nullfd); close(fd);
	    return 0;
	}
	if ( hasdata ) {
	    D(printf("Data read 0x%x..0x%x from 0x%x\n", lodata, hidata, offdata));
	    lseek(fd, offdata, 0);
	    if ( read(fd, lodata, hidata-lodata) != hidata-lodata ) {
		dl_error(0, "Could not read data segments");
		return 0;
	    }
	}
    }
    close(nullfd);
    return 1;
}
