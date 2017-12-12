EXEC = call_add1
LIB = ../../libdld.a
INCLUDE = ../../dld.h
CC= gcc
CFLAGS = -g -I../..

all:	${EXEC}

clean:
	rm -f ${EXEC} *.o

${LIB}:	../../dld.c $(INCLUDE)
	cd ../..; make ; cd test/add1

.c.o:
	${CC} -c ${CFLAGS} $*.c

call_add1: $(LIB) $(INCLUDE) add1.o call_add1.c
	${CC} ${CFLAGS} call_add1.c $(LIB) -o call_add1

