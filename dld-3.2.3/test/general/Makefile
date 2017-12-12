EXEC = dld-test
LIB = ../../libdld.a
OBJS =  hello.o print_arg.o read-a.out.o list-undefined.o get-sym.o need.o\
	test-define.o print_global.o remove.o
INCLUDE = ../../dld.h
CC= gcc
CFLAGS = -g -I../..

all:	${EXEC} ${OBJS} ${LIB}

clean:
	rm -f ${EXEC} ${OBJS} *.o

${LIB}: 
	cd ../..; make

hello.o: hello.c
	${CC} -c hello.c
.c.o:
	${CC} -c ${CFLAGS} $*.c

dld-test: $(LIB) $(INCLUDE) main.o
	${CC} ${CFLAGS} main.o $(LIB) -o dld-test


