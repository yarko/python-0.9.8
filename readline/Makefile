## -*- text -*- ####################################################
#								   #
# Makefile for readline and history libraries.			   #
#								   #
####################################################################

# Here is a rule for making .o files from .c files that doesn't force
# the type of the machine (like -sun3) into the flags.
.c.o:
	$(CC) -c $(CFLAGS) $(LOCAL_INCLUDES) \
		$(READLINE_DEFINES) $(CPPFLAGS) $*.c

# Destination installation directory.  The libraries are copied to DESTDIR
# when you do a `make install', and the header files to INCDIR/readline/*.h.
DESTDIR = /usr/local/lib
INCDIR = /usr/local/include

# Define TYPES as -DVOID_SIGHANDLER if your operating system uses
# a return type of "void" for signal handlers.
TYPES = -DVOID_SIGHANDLER

# Define USG as -DUSG if you are using a System V operating system.
#USG = -DUSG

# Define ALLOCA as -DHAVE_ALLOCA_H if your operating system requires
# you to #include <alloca.h> to use alloca().
ALLOCA = -DHAVE_ALLOCA_H

# HP-UX compilation requires the BSD library.
#LOCAL_LIBS = -lBSD

# Xenix compilation requires -ldir -lx
#LOCAL_LIBS = -ldir -lx

# Comment out "-DVI_MODE" if you don't think that anyone will ever desire
# the vi line editing mode and features.  Make sure to comment out the
# definition of VI if you remove the -DVI_MODE.
READLINE_DEFINES = $(TYPES) -DVI_MODE

DEBUG_FLAGS = -g
LDFLAGS = $(DEBUG_FLAGS) 
CFLAGS = $(DEBUG_FLAGS) $(USG) $(ALLOCA) -I.

# A good alternative is gcc -traditional.
#CC = gcc -traditional
CC = cc
RANLIB = /usr/bin/ranlib
AR = ar
RM = rm
CP = cp

LOCAL_INCLUDES = -I../

# (xmalloc used to be in ../malloc)
XMALLOC_C = xmalloc.c
XMALLOC_O = xmalloc.o

# (tilde used to be in ../glob)
TILDE_C = tilde.c
TILDE_O = tilde.o

CSOURCES = readline.c history.c funmap.c keymaps.c vi_mode.c \
	   emacs_keymap.c vi_keymap.c $(XMALLOC_C) $(TILDE_C)

HSOURCES = readline.h chardefs.h history.h keymaps.h
SOURCES  = $(CSOURCES) $(HSOURCES)

OBJECTS = readline.o vi_mode.o history.o funmap.o keymaps.o \
		$(XMALLOC_O) $(TILDE_O)

DOCSOURCE = doc/rlman.texinfo doc/rltech.texinfo doc/rluser.texinfo \
	    doc/hist.texinfo doc/hsuser.texinfo doc/hstech.texinfo
DOCOBJECT = doc/readline.dvi doc/history.dvi
DOCSUPPORT = doc/Makefile doc/texinfo.tex
DOCUMENTATION = $(DOCSOURCE) $(DOCOBJECT) $(DOCSUPPORT)

SUPPORT = COPYING Makefile $(DOCUMENTATION) ChangeLog examples

THINGS_TO_TAR = $(SOURCES) $(SUPPORT)

##########################################################################

all: libreadline.a

libreadline.a:	$(OBJECTS)
	$(RM) -f $@
	$(AR) clq $@ $(OBJECTS)
	-if [ -f "$(RANLIB)" ]; then $(RANLIB) libreadline.a; fi

readline: readline.h chardefs.h $(OBJECTS)
	$(CC) $(CFLAGS) $(CPPFLAGS) $(READLINE_DEFINES) \
	  $(LOCAL_INCLUDES) -DTEST -o readline readline.c vi_mode.o funmap.o \
	  $(TILDE_O) $(XMALLOC_O) keymaps.o history.o -L. -ltermcap

$(TILDE_O): $(TILDE_C)
	rm -f tilde.o
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $(TILDE_C)
	@-mv tilde.o $(TILDE_O)

$(XMALLOC_O): $(XMALLOC_C)
	rm -f $(XMALLOC_O)
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $(XMALLOC_C)
	@-mv xmalloc.o $(XMALLOC_O)

readline.o:	readline.c readline.h chardefs.h  keymaps.h history.h
history.o:	history.c history.h
vi_mode.o:	vi_mode.c
funmap.o:	funmap.c readline.h
keymaps.o:	keymaps.c emacs_keymap.c vi_keymap.c keymaps.h chardefs.h

documentation: force
	(cd doc; make)
force:

readline.tar:	$(THINGS_TO_TAR)
	tar -cf readline.tar $(THINGS_TO_TAR)

readline.tar.Z:	readline.tar
	compress -f readline.tar

install:	$(DESTDIR)/libreadline.a includes

# The rule for 'includes' is written funny so that the if statement
# always returns TRUE unless there really was an error installing the
# include files.
includes:
	if [ -r $(INCDIR)/readline ]; then \
	  :; \
	else \
	  mkdir $(INCDIR)/readline && chmod a+r $(INCDIR)/readline; \
	fi
	$(CP) readline.h keymaps.h chardefs.h $(INCDIR)/readline/
clean:
	rm -f $(OBJECTS) *.a
	(cd doc; make clean)

$(DESTDIR)/libreadline.a: libreadline.a
	-mv $(DESTDIR)/libreadline.a $(DESTDIR)/libreadline.old
	cp libreadline.a $(DESTDIR)/libreadline.a
	if [ -f "$(RANLIB)" ]; then $(RANLIB) -t $(DESTDIR)/libreadline.a; fi
