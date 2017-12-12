/***********************************************************
Copyright 1991, 1992 by Stichting Mathematisch Centrum, Amsterdam, The
Netherlands.
Additional Portions Copyright 1992 by Mark Anacker

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

/* PC module implementation

        This is my first crack at a low-level interface module for
        IBM-PC compatibles.  It makes heavy use of the bios routines
        that are available from Turbo C.
*/

#include <signal.h>
#include <string.h>
#include <setjmp.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#include <dir.h>
#include <io.h>

#ifdef MSDOS
#include <dos.h>
#include <fcntl.h>
#include <bios.h>
#include <mem.h>

struct timeval {
        unsigned long tv_sec;
        long    tv_usec;
        };

#endif

#include "allobjec.h"
#include "modsuppo.h"

typedef unsigned char byte;
typedef unsigned int uint;
typedef unsigned long ulong;

extern char *strerror PROTO((int));

/* PC methods */

/* bioscom - BIOS com port interface ----------------------------------------

        arguments:      cmd=0   set comm. parms. in char on port
                        cmd=1   send char to port
                        cmd=2   return char from port
                        cmd=3   return comm port status
-------------------------------------------------------------------------- */
static object *
pc_bioscom(self, args)          /* args = (cmd, port, char)     */
        object *self;
        object *args;
{
int cmd,port;
byte *achar;
register uint rv;
object *v;

        if (args == NULL || !is_tupleobject(args) || gettuplesize(args) != 3)
        {
                err_badarg();
                return NULL;
        }
        if (!getintarg(gettupleitem(args, 0), &cmd) ||
                !getintarg(gettupleitem(args, 1), &port) ||
                !getstrarg(gettupleitem(args,2), &achar))
                return NULL;

        v = newtupleobject(2);
        if (v == NULL)
                return NULL;

        rv = (uint) bioscom(cmd,*achar,port);
        settupleitem(v, 0, newintobject((ulong) (rv & 0xff)));
        settupleitem(v, 1, newintobject((ulong) ((rv & 0xff00) >> 8) ));
        return v;
}

/* biosdisk - BIOS disk services --------------------------------------------

        Interfaces to the low-level BIOS disk code.
-------------------------------------------------------------------------- */
static object *
pc_biosdisk(self, args)         /* args = (cmd, drive, head, track, sector, */
        object *self;           /*         num_sectors, buffer)             */
        object *args;
{
int cmd, drive, head, track, sector, nsects, rv;
void *buffer;

        if (args == NULL || !is_tupleobject(args) || gettuplesize(args) != 7)
        {
                err_badarg();
                return NULL;
        }
        if (!getintarg(gettupleitem(args, 0), &cmd) ||
                !getintarg(gettupleitem(args, 1), &drive) ||
                !getintarg(gettupleitem(args,2), &head) ||
                !getintarg(gettupleitem(args,3), &track) ||
                !getintarg(gettupleitem(args,4), &sector) ||
                !getintarg(gettupleitem(args,5), &nsects) ||
                !getpointarg(gettupleitem(args,6), &buffer))
                return NULL;

        rv = biosdisk(cmd,drive,head,track,sector,nsects,buffer);
        return(newintobject((long) rv));
}

/* biosequip - BIOS equipment scan ------------------------------------------

        returns a tuple of 5 numbers giving the display type, number of
        floppy drives, number of com ports, game ports, and printers.
-------------------------------------------------------------------------- */
static object *
pc_biosequip(self)              /* no args */
        object *self;
{
uint rv;
object *v;
struct eflag_st {
  unsigned int res1 : 4;
  unsigned int disp : 2;        /* display type */
  unsigned int flop : 2;        /* number of floppies */
  unsigned int res2 : 1;
  unsigned int ports : 3;       /* number of COM ports */
  unsigned int game : 1;        /* number of game ports */
  unsigned int res3 : 1;
  unsigned int print : 2;       /* number of printers */
} eflags;

        v = newtupleobject(5);
        if (v == NULL)
                return NULL;

        rv = (uint) biosequip();
        memcpy(&eflags,&rv,sizeof(rv));
        settupleitem(v, 0, newintobject((ulong) eflags.disp));
        settupleitem(v, 1, newintobject((ulong) (eflags.flop+1)));
        settupleitem(v, 2, newintobject((ulong) eflags.ports));
        settupleitem(v, 3, newintobject((ulong) eflags.game));
        settupleitem(v, 4, newintobject((ulong) eflags.print));
        return v;
}

/* biosmemory - BIOS memory size --------------------------------------------

        returns the number of Kbytes of low RAM
-------------------------------------------------------------------------- */
static object *
pc_biosmemory(self)             /* no args */
        object *self;
{
register uint rv;

        rv = (uint) biosmemory();
        return newintobject((long) rv);
}

/* biostime - BIOS timer count ----------------------------------------------

        arguments:      cmd=0   return ticks since midnight
                        cmd=1   set tick counter
*/
static object *
pc_biostime(self, args)
        object *self;
        object *args;                   /* args = (cmd, ticks) */
{
ulong   bcmd,btime;
object  *v;

        if ((!getlongarg(gettupleitem(args, 0), &bcmd)) ||
            (!getlongarg(gettupleitem(args,1), &btime)))
                return NULL;
        btime = (ulong) biostime(bcmd,btime);
        return newlongobject((long) btime);
}

/* biosprint - BIOS printer interface ---------------------------------------

        arguments:      cmd=0   send char to port
                        cmd=1   initialize port
                        cmd=2   return port status
-------------------------------------------------------------------------- */
static object *
pc_biosprint(self, args)                /* args = (cmd, port, char)     */
        object *self;
        object *args;
{
int cmd,port;
char achar[2];
register uint rv;

        if (args == NULL || !is_tupleobject(args) || gettuplesize(args) != 3)
        {
                err_badarg();
                return NULL;
        }
        if (!getintarg(gettupleitem(args, 0), &cmd) ||
                !getintarg(gettupleitem(args, 1), &port) ||
                !getstrarg(gettupleitem(args,2), &achar))
                return NULL;

        rv = (uint) biosprint(cmd,achar[0],port);
        return newintobject((long) rv);
}

/* bioskey - BIOS keyboard interface ----------------------------------------

        arguments:      cmd=0   return scan code, leave in buffer
                                (wait for key if buffer is empty)
                        cmd=1   return scan code, remove from buffer
                                (return 0 if buffer is empty)
                        cmd=2   return shift-state flags
-------------------------------------------------------------------------- */
static object *
pc_bioskey(self, args)          /* args = cmd   */
        object *self;
        object *args;
{
int cmd;
register uint rv;
object *v;

        if (!getintarg(args, &cmd))
                return NULL;
        rv = (uint) bioskey(cmd);
        v = newtupleobject(2);
        if (v == NULL)
                return NULL;

        settupleitem(v, 0, newintobject((ulong) (rv & 0xff)));
        settupleitem(v, 1, newintobject((ulong) ((rv & 0xff00) >> 8) ));
        return v;
}

static struct methodlist pc_methods[] = {
        {"bioscom",     pc_bioscom},
        {"biosdisk",    pc_biosdisk},
        {"biosequip",   pc_biosequip},
        {"biosmemory",  pc_biosmemory},
        {"biostime",    pc_biostime},
        {"biosprint",   pc_biosprint},
        {"bioskey",     pc_bioskey},
        {NULL,          NULL}            /* Sentinel */
};


void
initpc()
{
        object *m, *d, *v;

        m = initmodule("pc", pc_methods);
        d = getmoduledict(m);
}
