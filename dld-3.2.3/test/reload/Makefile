EXEC = reload reload-test
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

reload: $(LIB) $(INCLUDE) reload.o reload-test
	${CC} ${CFLAGS} reload.o $(LIB) -o reload

reload-test: reload-test.o
	ld -r reload-test.o /lib/libc.a -o reload-test

