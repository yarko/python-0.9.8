# You may have to change this definition of where dld is...
DLD=		../dld-3.2.3
OBJS=		dl_loadmod.o dl_getbinary.o dl_findlibs.o dl_error.o strerror.o
CFLAGS=		-g -I$(DLD)
CC=		gcc

libdl.a:	$(OBJS)
		ar crv libdl.a $(OBJS)
		ranlib libdl.a

$(OBJS):	dl.h
dl_loadmod.o:	$(DLD)/dld.h

clean::
		-rm -f *.o core [,#@]* *~ *.orig *.old *.bak *.BAK \
			nohup.out Part??

clobber::	clean
		-rm -f lib*.a tags TAGS

kit::
		makekit -m
