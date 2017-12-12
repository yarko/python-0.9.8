LIBDIR=..
CFLAGS=-g -I$(LIBDIR)
LIB=$(LIBDIR)/libdl.a
INC=$(LIBDIR)/dl.h

all: test sub.o sub2.o sub3.o test2 test3 test3sub1.o test3sub2.o

test: test.o $(LIB)
	cc test.o $(LIB) -lmld -o test

test2: test2.o $(LIB)
	cc test2.o $(LIB) -lmld -o test2

test3: test3.o $(LIB)
	cc test3.o $(LIB) -lmld -o test3

test3sub1.o: test3sub1.c
	cc -c -G 0 test3sub1.c -o test3sub1.o

test3sub2.o: test3sub2.c
	cc -c -G 0 test3sub2.c -o test3sub2.o

sub.o: sub.c
	cc -c -G 0 sub.c -o sub.o

sub2.o: sub2.c
	cc -c -G 0 sub2.c -o sub2.o

sub3.o: sub3.c
	cc -c -G 0 sub3.c -o sub3.o

$(LIB):
	( cd $(LIBDIR) ; make )
