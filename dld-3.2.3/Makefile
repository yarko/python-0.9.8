ARCHIVE = libdld.a
LIBS = dld.o find_exec.o define.o get_func.o get_symbol.o \
	list_undef.o mk_dummy.o ref.o ul_file.o ul_symbol.o \
	remove.o error.o
INCLUDE = dld.h defs.h
CC= gcc
CFLAGS = -g -I.

all:	${ARCHIVE}

libdld.a: ${LIBS} ${INCLUDES}
	rm -f libdld.a
	ar q libdld.a ${LIBS}
	ranlib libdld.a

clean:
	rm -f ${ARCHIVE} *.o
	cd test; make clean

.c.o:
	${CC} -c ${CFLAGS} $*.c

