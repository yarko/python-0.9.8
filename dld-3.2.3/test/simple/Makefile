EXEC = simple
LIB = ../../libdld.a
INCLUDE = ../../dld.h
CC= gcc
CFLAGS = -g -I../..

all:	${EXEC}

clean:
	rm -f ${EXEC} *.o

${LIB}:	../../dld.c $(INCLUDE)
	cd ../..; make

.c.o:
	${CC} -c ${CFLAGS} $*.c

simple:	$(LIB) $(INCLUDE) simple.c
	${CC} ${CFLAGS} simple.c $(LIB) -o simple
