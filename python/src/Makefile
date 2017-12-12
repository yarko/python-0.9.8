# /***********************************************************
# Copyright 1991, 1992 by Stichting Mathematisch Centrum, Amsterdam, The
# Netherlands.
# 
#                         All Rights Reserved
# 
# Permission to use, copy, modify, and distribute this software and its 
# documentation for any purpose and without fee is hereby granted, 
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in 
# supporting documentation, and that the names of Stichting Mathematisch
# Centrum or CWI not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior permission.
# 
# STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
# FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 
# ******************************************************************/


# Makefile for Python
# ===================

# Full building instructions are in ../misc/BUILD.  Read it now!

# If you are in a hurry, you can just edit this Makefile to choose the
# correct setting for SYSV below and run "make" in this directory.
# This should build a minimal Python interpreter.  Use it to run the
# Configure.py script, and then run "make" again to build a
# fully-configured Python interpreter.
#
# Installation can be done with "make install"; make sure the macros
# $(DESTDIR) etc. are defined correctly.
#
# Other useful utility targets include clean, clobber, depend, lint,
# tags and TAGS.
#
# Lines beginning with ## are directives for the Configure.py script;
# comments in the script explain their meaning.


# CFLAGS
# ======

# Here is the definition of CFLAGS.  Don't change it; edit ADDCFLAGS
# below to add flags.

CFLAGS=		$(THREAD_USE) $(ADDCFLAGS)


# Operating System Defines
# ========================

##group
# The 'architecture identifier' is a short string that characterizes
# the type of UNIX you are using.  Examples are sun4, sgi, vax, and hpux.
# If you don't know what to use, 'unknown' is just fine for now.
##edit What is your architecture identifier ?
ARCH=	    unknown
##endg

##exec sgi = (ARCH == 'sgi')
##exec sun4 = (ARCH == 'sun4')
##exec sun3 = (ARCH == 'sun3')
##exec hp = (ARCH == 'hpux')
##exec sun = (sun3 or sun4)

##if sgi or hp
##exec sysv = 1
##elif sun
##exec sysv = 0
##elifyes Is this a System-V (-like) system ? [yes]
##exec sysv = 1
##else
##exec sysv = 0
##endif

##if sysv
# OK, it's System-V (-like)
# This is the only line that should need to be edited manually!
##group
SYSVDEF=	-DSYSV
##endg
##else
# OK, it's BSD (-like)
##endif

##group
# Additional flags to the C compiler are defined in ADDCFLAG.
# Use this for instance to pass -g, -O, -D... or -I... to the compiler.
##edit
ADDCFLAGS=	
##endg

##group
##if not sysv
# Some non-System-V systems, e.g. SunOS, also define the argument of
# utime() as a struct.  (This is implied by SYSV.)
##ifyes Is your utime argument a struct ? [no]
#UTIMEDEF=	-DUTIME_STRUCT
##endif
##endif
##endg

##group
# If it exists, Python would like to provide an interface the Posix
# waitpid() function.  However, not all systems have it.
##ifno Does your system have a waitpid() system call ? [no]
WAITDEF=	-DNO_WAITPID
##endif
##endg

##group
# Python normally provides an interface to the symbolic link
# operations (lstat, symlink, readlink).  However, a few systems
# don't have these.
##ifno Does your system have symbolic links ? [yes]
#NOSYMLINKDEF=	-DNO_LSTAT
##endif
##endg

##group
# If your math library is not linked in the usual way (-lm), edit
# the following line.
##edit What is the linker option to link with the math library ?
LIBMATH=	-lm
##endg

##group
##if not (sun or hp)
# If you want the pwd and grp modules to use NIS (yellow pages),
# but the NIS versions of getpwent() etc. are not in the default C
# library, edit the following line.  (-lsun is for SGI)
##ifyes Do you want an extra library to link with NIS (yellow pages) ? [no]
##edit What is the linker option to link with NIS ?
#LIBYP=		-lsun
##endif
##endif
##endg


# Installation Options
# ====================

# Suggested installation pathnames (see "install" targets later):

##group
# If you want to use the "install" target, you must define the
# destination directory correctly.  The binary is installed as
# $(DESTDIR)/bin/python, the library files as $(DESTDIR)/lib/python/*,
# the man page as $(DESTDIR)/man/man1/python.1, etc.
# (If you don't like this arrangements, edit the Makefile manually.)
##editdir What is the destination directory ?
DESTDIR=/usr/local
##endg

BINDESTDIR=$(DESTDIR)/bin
BINDEST=$(BINDESTDIR)/python
MANDESTDIR=$(DESTDIR)/man/man1
MANDEST=$(MANDESTDIR)/python.1
LIBDESTDIR=$(DESTDIR)/lib
LIBDEST=$(LIBDESTDIR)/python
DOCDEST=$(LIBDEST)/doc
DEMODEST=$(LIBDEST)/demo

##group
# If you install manually, you may want to change DEFPYTHONPATH to
# reflect where you install the Python module library.
##edit
DEFPYTHONPATH=	.:$(LIBDEST):$(LIBDEST)/$(ARCH)
##endg


# Missing library functions
# =========================

##group
# Older UNIX systems often miss certain standard library functions.
# Source for (simple versions of) these is provided, you just have to
# turn the corresponding option on.  Leaving these options on
# regardless is usually fine, except where noted.
##endg

##group
# If your system does not have a strerror() function in the library,
# use one I wrote.
##ifyes Do you want to use my strerror() function? [yes]
STRERROR_SRC=  strerror.c
STRERROR_OBJ=  strerror.o
##endif
##endg

##group
# If your system does not have a fmod() function in the library, use
# the one I wrote.
##ifyes Do you want to use my fmod() function? [yes]
FMOD_SRC=  fmod.c
FMOD_OBJ=  fmod.o
##endif
##endg

##group
# If your system does not have a strtol() and a strtoul() function
# in the library, use the ones I wrote.
##ifyes Do you want to use my strtol() function? [yes]
STRTOL_SRC=  strtol.c
STRTOL_OBJ=  strtol.o
##endif
##endg

##if not sun
# *** DON'T USE THIS ON SPARCS (SunOS) -- IT DUMPS CORE ***
##group
# If your system does not have a strtod() function in the library,
# use a version which I got from comp.lang.sources (with a fix to the
# value of HUGE for IEEE machines provided by Tim Peters).
##ifyes Do you want to use my strtod() function? [no]
##echo PLEASE EDIT THE MACHINE DEPENDENCIES IN THE strtod.c SOURCE
#STRTOD_SRC=  strtod.c
#STRTOD_OBJ=  strtod.o
##endif
##endg
##endif

##group
# If your system does not have a getcwd() function in the library,
# but it does have a getwd() function, use the one I wrote.
# (If you don't have getwd() either, turn on the NO_GETWD #define in
# getcwd.c to let it fork a process to run pwd(1).)
##ifyes Do you want to use my getcwd() function? [no]
#GETCWD_SRC=  getcwd.c
#GETCWD_OBJ=  getcwd.o
##endif
##endg

##group
# If your signal() function believes signal handlers return int,
# turn on the following option.
##ifyes Do signal handlers on your system return int? [no]
#SIGTYPEDEF=	-DSIGTYPE=int
##endif
##endg


# Further porting hints
# =====================
#
# If you don't have the header file <string.h>, but you do have
# <strings.h>, create a file "string.h" in this directory which contains
# the single line "#include <strings.h>", and add "-I." to CFLAGS.
# If you don't have the functions strchr and strrchr, add definitions
# "-Dstrchr=index -Dstrrchr=rindex" to CFLAGS.  (NB: CFLAGS is not
# defined in this Makefile.)
#
# For AIX on an IBM R2, you need to add -DHAVE_STDLIB to CFLAGS;
# use cc for C compiler, I couldn't get it to work with cc89 or xlc.
#
# On older SunOS versions, strtod() is reported to set errno to ERANGE
# even though no overflow has in fact occurred.
# You have this problem if the first use of an innocent-looking literal
# like "0.0" in a Python program raises OverflowError.
# To cope, add -DBROKEN_STRTOD to CFLAGS (or define it in compile.c).
# (This disables overflow checking of floating point literals
# altogether, so take care!)
#
# If you have trouble compiling a required file named *module.c,
# (except sysmodule.c or bltinmodule.c), you can still try to build
# Python without that module -- edit the file out of the Makefile and
# remove the corresponding lines from config.c.  (Unfortunately if you
# have to do this for posixmodule.c, Configure.py won't run :-( ).
#
# If your C compiler thinks the switch in ceval.c is too big, try
# turning on the #define CASE_TOO_BIG.


# Configurable Options
# ====================
#
# Python can be configured to interface to various system libraries that
# are not available on all systems.  It is also possible to configure
# the input module to use the GNU Readline library for interactive
# input.  For each configuration choice you must answer the relevant
# question.  Note: you may also have to change a pathname and/or an
# architecture identifier that is hardcoded in the Makefile.
#
# Read the comments to determine if you can use the option.  (You can
# always leave all options off and build a minimal portable version of
# Python.)


# BSD Time Option
# ===============

##group
# The Python time module would like to provide functions millisleep()
# and millitimer() that can only be implemented if your system supports
# select() and gettimeofday().  If these aren't available, turn this
# option off.
##ifyes Does your system have select() and gettimeofday() ? [yes]
BSDTIMEDEF=	-DBSD_TIME
##else
# (Actually, you'll run in trouble with selectmodule.c as well... :-( )
##endif
##endg


# Times Option
# ============

##group
# The Python time module would like to provide the function times()
# that can only be implemented if your system supports the system call
# of the same name and the HZ parameter.  It is known to work on SYSV
# and SunOS, at least.
##ifyes Does your system have times() and HZ ? [yes]
TIMESDEF=	-DDO_TIMES
##endif
##endg


# Regular Expression Option
# =========================

##group
# The optional module regex provides Emacs-style regular expressions.
# On some very old systems the file "regexpr.c" doesn't compile
# and you have to disable this module.
##ifyes Do you want to use the regex module ? [yes]
RE_USE=	-DUSE_REGEX
RE_SRC=	regexpr.c regexmodule.c
RE_OBJ=	regexpr.o regexmodule.o
##endif
##endg


# GNU Readline Option
# ===================

##group
# With the GNU Readline library you can have full interactive command
# line editing and history in Python.
#
# The GNU Readline library source is distributed standard with Python,
# but you must still build it separately, and turn this option on,
# to benefit from it.  (Make sure that readline's configuration
# for ALLOCA matches Python's.)
##ifyes Do you want to configure the GNU readline option? [no]
##editfile Where is libreadline.a ?
#LIBREADLINE=	../../readline/libreadline.a
# You may have to fix the definition of LIBTERMCAP --
# on some systems it's called -ltermlib or some such.
##edit
#LIBTERMCAP=	-ltermcap
#RL_USE =	-DUSE_READLINE
#RL_LIBS=	$(LIBREADLINE)
#RL_LIBDEPS=	$(LIBREADLINE)

# Note that you must remove tokenizer.o if you turn this on

##if not (sgi or sun4)
# The readline library depends on the function alloca(), which is not
# provided in all systems.  You can use one written by Doug Gwyn.
##ifyes Do you want to link with Doug Gwyn's alloca ? [yes]
#C_ALLOCA=	-DC_ALLOCA
#ALLOCA_OBJ=	alloca.o
#ALLOCA_SRC=	alloca.c
##endif
##endif

##endif
##endg


# Additional Libraries
# ====================

##group
# Sometimes you want additional libraries added at the end of the link
# commands.  E.g. on the SGI it seems wise to link with -lmalloc,
# *unless* you are also using the threads option.
##ifyes Do you want additional libraries at the end of the link command? [no]
##edit What additional libraries do you want ?
#ADDLIBS=	 -lmalloc
##endif
##endg


# STDWIN Option
# =============

##group
# If you have the sources of STDWIN (by the same author) you can
# configure Python to incorporate the built-in module 'stdwin'.
# This requires a fairly recent version of STDWIN (0.9.7 or later).
##ifyes Do you want to configure the stdwin option ? [no]
##if ARCH == 'unknown'
##echo Note: you haven't set the architecture identifier properly.
# Continue this run of Configure.py, then run it again to fix it.
##endif
# Edit the STDWINDIR defition to reflect the top of the STDWIN source tree.
##editdir What is the toplevel directory of stdwin ?
#STDWINDIR=	../../stdwin
#LIBSTDWIN=	$(STDWINDIR)/Build/$(ARCH)/x11/lib/lib.a
# You may have to edit the LIBX11 defition to reflect the location of
# the X11 runtime library if it is non-standard.
# On an SGI, if you want to combine this with GL, use -lX11_s instead.
##edit What is the library name to link with X11 ?
#LIBX11 =	-lX11
#STDW_INCL=	-I$(STDWINDIR)/H
#STDW_USE=	-DUSE_STDWIN
#STDW_LIBS=	$(LIBSTDWIN)
#STDW_LIBDEPS=	$(LIBSTDWIN)
#STDW_SRC=	stdwinmodule.c
#STDW_OBJ=	stdwinmodule.o
##endif
##endg


# Amoeba Option
# =============

##group
# If you have the Amoeba 4.0 distribution (Beta or otherwise) you can
# configure Python to incorporate the built-in module 'amoeba'.
# (Python can also be built for native Amoeba, but it requires more
# work and thought, and I haven't done it for years.)
##ifyes Do you want to configure the Amoeba option ? [no]
# Edit the AMOEBADIR defition to reflect the top of the Amoeba source tree.
##editdir What is the Amoeba top level directory ?
#AMOEBADIR=	/usr/amoeba
# Edit the AM_CONF definition to reflect the machine/operating system
# configuration needed by Amoeba (this is the name of a subdirectory
# of $(AMOEBADIR)/conf/unix, e.g., vax.ultrix).
##edit What is the Amoeba architecture identifier ?
#AM_CONF=	mipseb.irix
#LIBAMUNIX=	$(AMOEBADIR)/conf/unix/$(AM_CONF)/lib/amunix/libamunix.a
#- NB: AM_INCL contains "-I/usr/include" in order to ensure that
#- header files duplicated by Amoeba are loaded from the native system,
#- not from the Amoeba headers.
#AM_INCL=	-I/usr/include -I$(AMOEBADIR)/src/h
#AM_USE =	-DUSE_AMOEBA
#AM_LIBDEPS=	$(LIBAMUNIX)
#AM_LIBS=	$(LIBAMUNIX)
#AM_SRC =	amoebamodule.c sc_interpr.c sc_errors.c
#AM_OBJ =	amoebamodule.o sc_interpr.o sc_errors.o
##endif
##endg


# DLD Option
# ==========

##if not sysv
##group
# Use the dld dynamic loading library (certain non-COFF systems only).
# When a module foo is imported, and it is not in the table of built-in
# modules, a search is made for a file "foomodule.o" in the Python path.
# (For SGI's see the DL option below.)
##ifyes Do you want to configure the DLD option ? [no]
##editdir
#DL_DIR= 	../../dl-dld
##editdir
#DLD_DIR=	../../dld-3.2.3
#DL_USE= 	-DUSE_DL
#DL_INCL=	-I$(DL_DIR)
#DL_LIBS=	-Bstatic $(DL_DIR)/libdl.a $(DLD_DIR)/libdld.a
##endif
##endg
##endif


# Silicon Graphics IRIS Options
# =============================
#
# The remaining options are only relevant if you are using a
# Silicon Graphics IRIS machine.  These have been tested with IRIX 3.3.1
# on a 4D/25 and more recently with IRIX 4.0.{2,5} on a 4D/35.
# If you combine these with the STDWIN option above, you
# may want to change "-lX11" into "-lX11_s".


##if not sgi
##group
# Since this doesn't seem to be an SGI system I'll skip the SGI questions.
##endg
##else

##group
# There are some options that are too esoteric to consider normally:
# The NASA Panel library, 4D/25 audio, SV (video).  These are normally
# skipped.
##ifyes Do you want to see *all* options, even obsolete ones? [no]
##exec special = 1
##else
##exec special = 0
##endif
##endg


# DL Option
# =========

##group
# Use Jack's dynamic loading library (SGI IRIX only).
# When a module foo is imported, and it is not in the table of built-in
# modules, a search is made for a file "foomodule.o" in the Python path.
##ifyes Do you want to configure the DL option ? [no]
##editdir
#DL_DIR =	../../dl
#DL_USE =	-DUSE_DL
#DL_INCL=	-I$(DL_DIR)
#DL_LIBS=	$(DL_DIR)/libdl.a -lmld
##endif
##endg


# GL Option
# =========

##group
# This option incorporates the built-in module 'gl', which provides a
# complete interface to the Silicon Graphics GL library.  It adds
# about 70K to the Python text size and about 260K to the unstripped
# binary size.
#
# If you choose this option, also choose the Font Manager option,
# unless you are building on an old IRIX system (pre-3.3).
##ifyes Do you want to configure the GL option ? [yes]
#GL_USE =	-DUSE_GL
#GL_LIBDEPS=	
#GL_LIBS=	-lgl_s
#GL_SRC =	glmodule.c cgensupport.c
#GL_OBJ =	glmodule.o cgensupport.o
##endif
##endg

# NOTE WHEN BUILDING FOR THE FIRST TIME:
# There is a circular dependency in the build process: you need to have
# a working Python interpreter before you can build a Python interpreter
# that incorporates the 'gl' module -- the source file 'glmodule.c' is
# not distributed (it's about 140K!) and a Python script is used to
# create it.  Thus, you first have to build python without the the GL
# and Panel options, then edit the Makefile to turn them (or at least GL)
# on and rebuild.  You may also have to set PYTHONPATH to point to
# the place where the module library is for the generation script to
# work.
# (Since building instructions require you to build a minimal
# interpreter first anyway, to run Configure.py, this won't be a
# problem in practice any more.)


# Font Manager Option
# ===================

##group
# This option incorporates the built-in module 'fm', which provides a
# complete interface to the Silicon Graphics Font Manager.
# This requires the GL option.
##ifyes Do you want to configure the FM option ? [yes]
#FM_USE =	-DUSE_FM
#FM_LIBDEPS=
#FM_LIBS=	-lfm_s
#FM_SRC =	fmmodule.c
#FM_OBJ =	fmmodule.o
##endif
##endg


# IMGFILE Option
# ==============

##group
# This option incorporates the built-in module 'imgfile', which provides
# a (simple) interface to read and write files in SGI's "image" format
# (usually these have an extension of ".rgb".
##ifyes Do you want to configure the imgfile module? [no]
#IMGFILE_USE=	-DUSE_IMGFILE
#IMGFILE_OBJ=	imgfilemodule.o
#IMGFILE_SRC=	imgfilemodule.c
#IMGFILE_LIBS=	-limage
##endif
##endg


# FORMS Option
# ============

##group
# If you have source for Mark Overmars' FORMS library, you can configure
# Python to incorporate the built-in module 'fl', which provides a
# fairly complete interface to the FORMS Library.  We find that FORMS
# is a good alternative to the NASA Panel Library (the next option).
# For more info about FORMS, write to markov@cs.ruu.nl.
#
# NB: This options requires the GL and FM options.
#     This was tested with FORMS version 2.1.
##ifyes Do you want to configure the FORMS option ? [no]
# Edit the FORMS variable to point to the source subdirectory of the
# FORMS distribution.
##editdir
#FORMS=		/ufs/guido/src/forms/FORMS
#FL_USE= 	-DUSE_FL
#FL_LIBDEPS=	$(FORMS)/libforms.a
#FL_INCL=	-I$(FORMS)
#FL_LIBS=	$(FORMS)/libforms.a
#FL_SRC= 	flmodule.c
#FL_OBJ= 	flmodule.o
##endif
##endg


##if special
# Panel Option
# ============

##group
# If you have source to the NASA Ames Panel Library, you can configure
# Python to incorporate the built-in module 'pnl', which is used byu
# the standard module 'panel' to provide an interface to most features
# of the Panel Library.  This option requires that you also turn on the
# GL option.  It adds about 100K to the Python text size and about 160K
# to the unstripped binary size.  This requires Panel Library version 9.7
# (for lower versions you may have to remove some functionality -- send
# me the patches if you bothered to do this).
#
# Note for gcc users: panelmodule.c cannot be compiled with gcc because
# of a declaration for calloc() in panel.h that isn't compatible with
# Standard C.
# You can either fix the header file or compile panelmodule.c with cc.
# (Using gcc -traditional won't work because the SGI header files
# contain modernisms.)
##ifyes Do you want to configure the PANEL option ? [no]
# Edit the PANELDIR definition to point to the top-level directory
# of the Panel distribution tree.
##editdir
#PANELDIR=	/usr/people/guido/src/pl
#PANELLIBDIR=	$(PANELDIR)/library
#LIBPANEL=	$(PANELLIBDIR)/lib/libpanel.a
#PANEL_USE=	-DUSE_PANEL
#PANEL_INCL=	-I$(PANELLIBDIR)/include
#PANEL_LIBDEPS=	$(LIBPANEL)
#PANEL_LIBS=	$(LIBPANEL)
#PANEL_SRC=	panelmodule.c
#PANEL_OBJ=	panelmodule.o
##endif
##endg
##endif


##if special
# Audio Option
# ============

##group
# This option lets you play with /dev/audio on the IRIS 4D/25.
# It incorporates the built-in module 'audio'.
# (This is not a very good audio device.  For a better one, see AL below.)
# Warning: using the asynchronous I/O facilities of this module can
# create a second 'thread', which looks in the listings of 'ps' like a
# forked child.  However, it shares its address space with the parent.
#
# Uncomment the following block to use the Audio option.
##ifyes Do you wan to configure the 4D/25 audio option ? [no]
#AUDIO_USE=	-DUSE_AUDIO
#AUDIO_SRC=	audiomodule.c asa.c
#AUDIO_OBJ=	audiomodule.o asa.o
##endif
##endg
##endif


# AL Option
# =========

##group
# This option interfaces with /dev/audio on the IRIS 4D/35 and Indigo.
#
# Uncomment the following block to use the AL option.
##ifyes Do you want to configure the Indigo and 4D/35 AL option ? [yes]
#AL_USE= 	-DUSE_AL
#AL_LIBDEPS=	/usr/lib/libaudio.a
#AL_LIBS=	-laudio
#AL_SRC= 	almodule.c
#AL_OBJ= 	almodule.o
##endif
##endg


# JPEG Option
# ===========

##group
# This option enables access to the JPEG coder/decoder through the
# jpeg module.  You need the JPEG software as modified by Jack at CWI
# for this to work.
##ifyes Do you want to configure the JPEG option ? [no]
#JPEG_USE=	-DUSE_JPEG
##editdir
#JPEG_DIR=	/ufs/jack/src/av/jpeg
#JPEG_LIBS=	$(JPEG_DIR)/incore/libmjpeg.a $(JPEG_DIR)/libjpeg.a
#JPEG_LIBDEPS=	$(JPEG_LIBS)
#JPEG_SRC=	jpegmodule.c
#JPEG_OBJ=	jpegmodule.o
#JPEG_INCL=	-I$(JPEG_DIR)
##endif
##endg


# CD Option
# =========

##group
# This option interfaces with the CDROM drive on an Iris 4D system.
##ifyes Do you want to configure the CD option ? [no]
#CD_USE= 	-DUSE_CD
#CD_LIBDEPS=	/usr/lib/libcdaudio.a /usr/lib/libds.a
#CD_LIBS=	-lcdaudio -lds
#CD_SRC= 	cdmodule.c
#CD_OBJ= 	cdmodule.o
##endif
##endg


##if special
# SV Option
# =========

##group
# This option interfaces with the Video board on an Iris Indigo.
# It requires Irix 4.0.5 or higher.
##ifyes Do you want to configure the SV option ? [no]
#SV_USE= 	-DUSE_SV
#SV_LIBDEPS=	/usr/lib/libsvideo.a /usr/lib/libXext.a
#SV_LIBS=	-lsvideo -lXext
#SV_SRC= 	svmodule.c
#SV_OBJ= 	svmodule.o
##endif
##endg
##endif


##if special
# CL Option
# =========

##group
# This option interfaces with the Compression Library on the Iris Indigo.
# It requires Irix 4.0.5 or higher.
##ifyes Do you want to configure the CL option ? [no]
##editdir
#CL_DIR=	/ufs/sjoerd/ansjovis/clNEW
#CL_USE= 	-DUSE_CL
#CL_LIBDEPS=	$(CL_DIR)/libcl.a
#CL_LIBS=	-L$(CL_DIR) -lcl
#CL_SRC= 	clmodule.c
#CL_OBJ= 	clmodule.o
##endif
##endg
##endif


# Thread Option
# =============

##group
# On SGI systems (Irix 4.0.x) you can extend Python with multiple threads.

# Uncomment these lines AND RECOMPILE EVERYTHING to support threads:
##ifyes Do you want to configure the thread option ? [no]
##echo Better use "make clean" to remove all objects now!!!
#THREAD_USE=	-DUSE_THREAD
##edit Add -DDEBUG if you want special thread debugging
#THREAD_DEBUG=
#THREAD_SRC=	threadmodule.c thread.c
#THREAD_OBJ=	threadmodule.o thread.o
#THREAD_LIBS=	-lmpc
#THREAD_LIBDEPS= /usr/lib/libmpc.a
##endif
##endg

# This option almost worked for SunOS, but there's a catch: after exiting
# it leaves the tty in non-blocking mode, which is quite antisocial.
# Also, it seems to interact badly with readline, stdwin and interrupts.
# A possibility would be to build a special threading python, to be
# used only for daemon processes.
# Try these alternatives (manually edit the Makefile!):

#THREAD_LIBS=	-lnbio -llwp
#THREAD_LIBDEPS= /usr/lib/libnbio.a /usr/lib/liblwp.a

##endif sgi


# NIS Option
# ==========

##group
# This enables the nis module (NIS, formerly Yellow Pages).
# It implements the functions ypcat, ypmatch and ypmaps
# as nis.cat, nis.match and nis.maps.
##ifyes Do you want to configure the NIS option ? [no]
# Note: on an SGI you may need to compile nismodule.o with cc -cckr
# and you must link with -lsun (see LIBYP above).
#NIS_USE=	-DUSE_NIS
#NIS_SRC=	nismodule.c
#NIS_OBJ=	nismodule.o
##endif
##endg


##group
# Optional module rotor
##ifyes Do you want to configure the ROTOR option ? [no]
#ROTOR_USE=	-DUSE_ROTOR
#ROTOR_SRC=	rotormodule.c
#ROTOR_OBJ=	rotormodule.o
#ROTOR_LIBS=
#ROTOR_LIBDEPS=
##endif
##endg


##group
# Optional module fcntl
##ifyes Do you want to configure the FCNTL option ? [no]
#FCNTL_USE=	-DUSE_FCNTL
#FCNTL_SRC=	fcntlmodule.c
#FCNTL_OBJ=	fcntlmodule.o
#FCNTL_LIBS=
#FCNTL_LIBDEPS=
##endif
##endg


##group
# Optional module audioop
##ifyes Do you want to configure the AUDIOOP option ? [no]
#AUDIOOP_USE=	-DUSE_AUDIOOP
#AUDIOOP_SRC=	audioopmodule.c
#AUDIOOP_OBJ=	audioopmodule.o
#AUDIOOP_LIBS=
#AUDIOOP_LIBDEPS=
##endif
##endg


##group
# Optional module dbm
##ifyes Do you want to configure the DBM option ? [no]
#DBM_USE=	-DUSE_DBM
#DBM_SRC=	dbmmodule.c
#DBM_OBJ=	dbmmodule.o
#DBM_LIBS=
#DBM_LIBDEPS=
##endif
##endg


##group
# Optional module sgi
##ifyes Do you want to configure the SGI option ? [no]
#SGI_USE=	-DUSE_SGI
#SGI_SRC=	sgimodule.c
#SGI_OBJ=	sgimodule.o
#SGI_LIBS=
#SGI_LIBDEPS=
##endif
##endg


##group
# Optional module strop
##ifyes Do you want to configure the STROP option ? [yes]
STROP_USE=	-DUSE_STROP
STROP_SRC=	stropmodule.c
STROP_OBJ=	stropmodule.o
STROP_LIBS=
STROP_LIBDEPS=
##endif
##endg


##group
# Optional module sunaudiodev
##ifyes Do you want to configure the SUNAUDIODEV option ? [no]
#SUNAUDIODEV_USE=	-DUSE_SUNAUDIODEV
#SUNAUDIODEV_SRC=	sunaudiodevmodule.c
#SUNAUDIODEV_OBJ=	sunaudiodevmodule.o
#SUNAUDIODEV_LIBS=
#SUNAUDIODEV_LIBDEPS=
##endif
##endg


# IMAGEOP Option
# ==============
#
##group
# This enables the imageop module.
##ifyes Do you want to configure the IMAGEOP option ? [no]
#IMAGEOP_USE=	-DUSE_IMAGEOP
#IMAGEOP_SRC=	imageopmodule.c
#IMAGEOP_OBJ=	imageopmodule.o
#IMAGEOP_LIBS=
#IMAGEOP_LIBDEPS=
##endif
##endg


# MPZ Option
# ==========
#
##group
# This option enables access to the MPZ routines provided by GNU MP
# mpz module.  This mpz interface was used together with GNU MP 1.2
##ifyes Do you want to configure the MPZ option ? [no]
#MPZ_USE=	-DUSE_MPZ
##editdir
#MPZ_DIR=	/ufs/jh/src/gmp-1.2
#MPZ_LIBS=	$(MPZ_DIR)/libgmp.a
#MPZ_LIBDEPS=	$(MPZ_LIBS)
#MPZ_SRC=	mpzmodule.c
#MPZ_OBJ=	mpzmodule.o
#MPZ_INCL=	-I$(MPZ_DIR)
##endif
##endg


# MD5 Option
# ==========
#
##group
# This option enables access to the MD5 routines provided by GNU MP
# md5 module.  This md5 interface was used together with GNU MP 1.2
##ifyes Do you want to configure the MD5 option ? [no]
#MD5_USE=	-DUSE_MD5
##editdir
#MD5_DIR=	/ufs/jh/src/md5
#MD5_LIBS=	$(MD5_DIR)/md5.o
#MD5_LIBDEPS=	$(MD5_LIBS)
#MD5_SRC=	md5module.c
#MD5_OBJ=	md5module.o
#MD5_INCL=	-I$(MD5_DIR)
##endif
##endg


# -- ADDMODULE MARKER -- Addmodule.sh inserts new modules here


# Major Definitions
# =================

STANDARD_OBJ=	acceler.o $(ALLOCA_OBJ) bltinmodule.o ceval.o classobject.o \
		compile.o dictobject.o errors.o fgetsintr.o \
		fileobject.o floatobject.o $(FMOD_OBJ) frameobject.o \
		funcobject.o $(GETCWD_OBJ) \
		graminit.o grammar1.o import.o \
		intobject.o intrcheck.o longobject.o listnode.o listobject.o \
		marshal.o mathmodule.o methodobject.o modsupport.o \
		moduleobject.o node.o object.o parser.o \
		parsetok.o posixmodule.o pwdmodule.o pythonrun.o \
		$(RE_OBJ) \
		selectmodule.o socketmodule.o $(STRERROR_OBJ) \
		stringobject.o $(STRTOL_OBJ) $(STRTOD_OBJ) structmember.o \
		structmodule.o sysmodule.o \
		timemodule.o tokenizer.o traceback.o \
		tupleobject.o typeobject.o

STANDARD_SRC=	acceler.c $(ALLOCA_SRC) bltinmodule.c ceval.c classobject.c \
		compile.c dictobject.c errors.c fgetsintr.c \
		fileobject.c floatobject.c $(FMOD_SRC) frameobject.c \
		funcobject.c $(GETCWD_SRC) \
		graminit.c grammar1.c import.c \
		intobject.c intrcheck.c listnode.c listobject.c longobject.c \
		marshal.c mathmodule.c methodobject.c modsupport.c \
		moduleobject.c node.c object.c parser.c \
		parsetok.c posixmodule.c pwdmodule.c pythonrun.c \
		$(RE_SRC) \
		selectmodule.c socketmodule.c $(STRERROR_SRC) \
		stringobject.c $(STRTOL_SRC) $(STRTOD_SRC) structmember.c \
		structmodule.c sysmodule.c \
		timemodule.c tokenizer.c traceback.c \
		tupleobject.c typeobject.c

CONFIGDEFS=	$(STDW_USE) $(AM_USE) $(AUDIO_USE) $(GL_USE) $(FM_USE) \
		$(MD5_USE) \
		$(MPZ_USE) \
		$(IMAGEOP_USE) \
		$(SUNAUDIODEV_USE) \
		$(STROP_USE) \
		$(SGI_USE) \
		$(DBM_USE) \
		$(AUDIOOP_USE) \
		$(FCNTL_USE) \
		$(ROTOR_USE) \
		$(FL_USE) $(IMGFILE_USE) $(PANEL_USE) $(AL_USE) $(JPEG_USE) \
		$(CD_USE) $(SV_USE) $(CL_USE) $(NIS_USE) $(RE_USE) \
		'-DPYTHONPATH="$(DEFPYTHONPATH)"'

CONFIGINCLS=	$(STDW_INCL)

LIBDEPS=	libpython.a $(STDW_LIBDEPS) $(AM_LIBDEPS) \
		$(MD5_LIBDEPS) \
		$(MPZ_LIBDEPS) \
		$(IMAGEOP_LIBDEPS) \
		$(SUNAUDIODEV_LIBDEPS) \
		$(STROP_LIBDEPS) \
		$(SGI_LIBDEPS) \
		$(DBM_LIBDEPS) \
		$(AUDIOOP_LIBDEPS) \
		$(FCNTL_LIBDEPS) \
		$(ROTOR_LIBDEPS) \
		$(GL_LIBDEPS) $(FM_LIBDEPS) $(PANEL_LIBDEPS) \
		$(RL_LIBDEPS) $(FL_LIBDEPS) $(AL_LIBDEPS) \
		$(JPEG_LIBDEPS) $(CD_LIBDEPS) $(SV_LIBDEPS) \
		$(CL_LIBDEPS) $(THREAD_LIBDEPS)

# NB: the ordering of some items in LIBS is magically significant!
LIBS=		libpython.a $(STDW_LIBS) $(AM_LIBS) \
		$(MD5_LIBS) \
		$(MPZ_LIBS) \
		$(IMAGEOP_LIBS) \
		$(SUNAUDIODEV_LIBS) \
		$(STROP_LIBS) \
		$(SGI_LIBS) \
		$(DBM_LIBS) \
		$(AUDIOOP_LIBS) \
		$(FCNTL_LIBS) \
		$(ROTOR_LIBS) \
		$(PANEL_LIBS) $(FL_LIBS) $(RL_LIBS) \
		$(LIBMATH) $(LIBYP) $(AL_LIBS) \
		$(JPEG_LIBS) $(CD_LIBS) $(SV_LIBS) $(CL_LIBS) $(IMGFILE_LIBS) \
		$(DL_LIBS) $(THREAD_LIBS) \
		$(FM_LIBS) $(GL_LIBS) $(LIBX11) $(LIBTERMCAP) \
		$(ADDLIBS)

LIBOBJECTS=	$(STANDARD_OBJ) $(STDW_OBJ) $(AM_OBJ) $(AUDIO_OBJ) \
		$(MD5_OBJ) \
		$(MPZ_OBJ) \
		$(IMAGEOP_OBJ) \
		$(SUNAUDIODEV_OBJ) \
		$(STROP_OBJ) \
		$(SGI_OBJ) \
		$(DBM_OBJ) \
		$(AUDIOOP_OBJ) \
		$(FCNTL_OBJ) \
		$(ROTOR_OBJ) \
		$(FL_OBJ) $(GL_OBJ) $(FM_OBJ) $(IMGFILE_OBJ) $(PANEL_OBJ) \
		$(AL_OBJ) $(JPEG_OBJ) $(CD_OBJ) $(SV_OBJ) $(CL_OBJ) \
		$(THREAD_OBJ) $(NIS_OBJ)

LIBSOURCES=	$(STANDARD_SRC) $(STDW_SRC) $(AM_SRC) $(AUDIO_SRC) \
		$(MD5_SRC) \
		$(MPZ_SRC) \
		$(IMAGEOP_SRC) \
		$(SUNAUDIODEV_SRC) \
		$(STROP_SRC) \
		$(SGI_SRC) \
		$(DBM_SRC) \
		$(AUDIOOP_SRC) \
		$(FCNTL_SRC) \
		$(ROTOR_SRC) \
		$(FL_SRC) $(GL_SRC) $(FM_SRC) $(IMGFILE_SRC) $(PANEL_SRC) \
		$(AL_SRC) $(JPEG_SRC) $(CD_SRC) $(SV_SRC) $(CL_SRC) \
		$(THREAD_SRC) $(NIS_SRC)

OBJECTS=	pythonmain.o config.o

SOURCES=	$(LIBSOURCES) pythonmain.c config.c

GENOBJECTS=	acceler.o fgetsintr.o grammar1.o \
		intrcheck.o listnode.o node.o parser.o \
		parsetok.o tokenizer.o bitset.o \
		firstsets.o grammar.o metagrammar.o pgen.o \
		pgenmain.o printgrammar.o

GENSOURCES=	acceler.c fgetsintr.c grammar1.c \
		intrcheck.c listnode.c node.c parser.c \
		parsetok.c tokenizer.c bitset.c \
		firstsets.c grammar.c metagrammar.c pgen.c \
		pgenmain.c printgrammar.c


# Main Targets
# ============

python:		libpython.a $(OBJECTS) $(LIBDEPS) Makefile
		$(CC) $(CFLAGS) $(OBJECTS) $(LIBS) -o @python
		mv @python python

libpython.a:	$(LIBOBJECTS)
		-rm -f @lib
		ar cr @lib $(LIBOBJECTS)
		@echo '(never mind if ranlib is not found -- probably SYSV)'
		-(ranlib @lib)
		mv @lib libpython.a

python_gen:	$(GENOBJECTS) $(RL_LIBDEPS)
		$(CC) $(CFLAGS) \
		$(GENOBJECTS) $(RL_LIBS) $(LIBTERMCAP) -o python_gen


# Utility Targets
# ===============

# Don't take the output from lint too seriously.  I have not attempted
# to make Python lint-free.  But I do use function prototypes.

LINTFLAGS=	-h

LINTCPPFLAGS=	$(CONFIGDEFS) $(CONFIGINCLS) $(SYSVDEF) $(UTIMEDEF) \
		$(AM_INCL) $(FL_INCL) $(PANEL_INCL) \
		$(MPZ_INCL) $(MD5_INCL) \
		$(THREAD_USE) $(ADDCFLAGS)

LINT=		lint

lint::		$(SOURCES)
		$(LINT) $(LINTFLAGS) $(LINTCPPFLAGS) $>

lint::		$(GENSOURCES)
		$(LINT) $(LINTFLAGS) $>

# Generating dependencies is only necessary if you intend to hack Python.
# You may change $(MKDEP) to your favorite dependency generator (it should
# edit the Makefile in place).

MKDEP=		mkdep

depend::	$(SOURCES) $(GENSOURCES)
		$(MKDEP) $(LINTCPPFLAGS) $>

# You may change $(CTAGS) and $(ETAGS) to suit your taste...

CTAGS=		ctags -t -w
ETAGS=		etags -t

HEADERS=	*.h

tags:		$(SOURCES) $(GENSOURCES) $(HEADERS)
		$(CTAGS) $>

TAGS:		$(SOURCES) $(GENSOURCES) $(HEADERS)
		$(ETAGS) $>

clean::
		-rm -f *.o [,#@]* *~ *.orig *.old *.bak *.pyc core nohup.out

clobber::	clean
		-rm -f glmodule.c
		-rm -f python python_gen libpython.a tags TAGS


# Some people insist that a Makefile contain an 'install' target.
# Here's a minimal one that installs the interpreter, manual page and
# library modules (ands hints how you might install the demos and docs).
#
# I don't use a fancy "install" program since those tend to have
# different call formats on AT&T and BSD systems.
#
# If you are doing this as a super-user you may want to chown the
# installed files to bin or some other innocent user.
#
# The $(*DEST) macros are defined earlier in the Makefile.

# File modes are set to 644 (data) or 755 (executables and directories).
DPERM=644
XPERM=755

install: install_bin install_man install_lib
		@echo "To install the demo programs: make install_demo"
		@echo "To build+install the LaTeX documents: make install_doc"

install_bin:	python
		cp python $(BINDEST)
		chmod $(XPERM) $(BINDEST)
# XXX What if $(BINDEST) already exists and is being used?

install_man:	../misc/python.man
		cp ../misc/python.man $(MANDEST)
		chmod $(DPERM) $(MANDEST)

install_lib:	../lib
		-mkdir $(LIBDEST)
		-chmod $(XPERM) $(LIBDEST)
		cp -r ../lib/* $(LIBDEST)
		chmod $(DPERM) $(LIBDEST)/*
# XXX This should ideally also create most of the .pyc files...

install_demo::
		-mkdir $(DEMODEST)
		cp -r ../demo/* $(DEMODEST)

install_doc::
		cd ../doc; make all; make clean
		-mkdir $(DOCDEST)
		cp ../doc/* $(DOCDEST)


# Build Special Objects
# =====================

# You may change $(COMPILE) to reflect the default .c.o rule...

COMPILE=	$(CC) $(CFLAGS) -c

amoebamodule.o:	amoebamodule.c
		$(COMPILE) $(AM_INCL) $*.c

config.o:	config.c Makefile libpython.a
		$(COMPILE) $(CONFIGDEFS) $(CONFIGINCLS) $*.c

clmodule.o:	clmodule.c
		$(COMPILE) -I$(CL_DIR) $*.c

fgetsintr.o:	fgetsintr.c
		$(COMPILE) $(SIGTYPEDEF) $*.c

flmodule.o:	flmodule.c
		$(COMPILE) $(FL_INCL) $*.c

glmodule.o:	glmodule.c
		$(COMPILE) -cckr $*.c

import.o:	import.c
		$(COMPILE) $(DL_USE) $(DL_INCL) $*.c

intrcheck.o:	intrcheck.c
		$(COMPILE) $(SIGTYPEDEF) $*.c

jpegmodule.o:	jpegmodule.c
		$(COMPILE) $(JPEG_INCL) $*.c

panelmodule.o:	panelmodule.c
		$(COMPILE) $(PANEL_INCL) $*.c

posixmodule.o:	posixmodule.c
		@echo "(If building posixmodule fails, try enabling SYSVDEF)"
		$(COMPILE) $(SYSVDEF) $(TIMESDEF) $(UTIMEDEF) \
			   $(NOSYMLINKDEF) $(WAITDEF) $*.c

sc_interpr.o:	sc_interpr.c
		$(COMPILE) $(AM_INCL) $*.c

sc_error.o:	sc_error.c
		$(COMPILE) $(AM_INCL) $*.c

stdwinmodule.o:	stdwinmodule.c
		$(COMPILE) $(STDW_INCL) $*.c

svmodule.o:	svmodule.c
		$(COMPILE) $(GL_USE) $*.c

thread.o:	thread.c
		$(COMPILE) $(DL_USE) $(THREAD_DEBUG) $*.c

timemodule.o:	timemodule.c
		$(COMPILE) $(SIGTYPEDEF) $(BSDTIMEDEF) $*.c

tokenizer.o:	tokenizer.c
		$(COMPILE) $(RL_USE) $*.c

mpzmodule.o:	mpzmodule.c
		$(COMPILE) $(MPZ_INCL) $*.c

md5module.o:	md5module.c
		$(COMPILE) $(MD5_INCL) $*.c

# These targets shouldn't be deleted when the rule building them failse:
.PRECIOUS:	python libpython.a glmodule.c graminit.c graminit.h


# Generated Sources
# =================
#
# Some source files are (or may be) generated.
# The rules for doing so are given here.

# Build "glmodule.c", the GL interface.
# See important note at "GL Option" above.
# You may have to set and export PYTHONPATH for this to work.
# Ignore the messages emitted by the cgen.py script as long as its exit
# status is zero.
# Also ignore the warnings emitted while compiling glmodule.c; it works.

glmodule.c:	cstubs cgen.py
		PYTHONPATH=../lib python $> >@glmodule.c
		mv @glmodule.c glmodule.c

# The dependencies for graminit.[ch] are not turned on in the
# distributed Makefile because the files themselves are distributed.
# Turn them on if you want to hack the grammar.

#graminit.c:	Grammar python_gen
#		python_gen Grammar

# One call to python_gen writes both files, so here's a fake dependency:
#graminit.h:	graminit.c


##group
# ----------------------------------------------- #
# You have completed the configuration questions. #
# Now run "make" and sit back...                  #
# ----------------------------------------------- #
##endg

# DO NOT PUT ANYTHING AFTER THIS LINE, IT WILL GO AWAY.
