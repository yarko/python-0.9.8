# Debugging:
# CFLAGS=-g -DDEBUG
# LIB=libdl_g.a
# Production:
CFLAGS=-O
LIB=libdl.a
LIBOBJS=dl_ldnfilep.o dl_ldzfilep.o dl_ldfile.o dl_loadmod.o dl_linkfile.o \
	dl_gettime.o dl_findcache.o dl_findlibs.o dl_error.o \
	dl_getbinary.o dl_checkrange.o dl_remsym.o
LIBSRCS=dl_ldnfilep.c dl_ldzfilep.c dl_ldfile.c dl_loadmod.c dl_linkfile.c \
	dl_gettime.c dl_findcache.c dl_findlibs.c dl_error.c \
	dl_getbinary.c dl_checkrange.c dl_remsym.c
TESTSRC=test/Makefile test/test.c test/sub.c test/sub2.c test/sub.libs
SUBDIRS=test
LIBALL=README Makefile dl.h dl.man dlother.man $(LIBSRCS) $(TESTSRC)

$(LIB): $(LIBOBJS)
	rm -f $(LIB)
	ar cr $(LIB) $(LIBOBJS)

$(LIBOBJS): dl.h

dl.shar: $(LIBALL)
	shar $(SUBDIRS) $(LIBALL) > dl.shar

dl.tar.Z: $(LIBALL)
	tar cf dl.tar $(LIBALL)
	compress dl.tar
