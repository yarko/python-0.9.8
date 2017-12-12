EXEC = overlay
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

overlay: $(LIB) $(INCLUDE) overlay.c chain1.o chain2.o chain3.o 
	${CC} ${CFLAGS} -fwritable-strings overlay.c $(LIB) -o overlay

