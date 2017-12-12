# You may have to change this definition of where dld is...
DLD=	../../dld-3.2.3
DL=	..
CFLAGS=	-g -I$(DL)
LIBS=	$(DL)/libdl.a $(DLD)/libdld.a
CC=	gcc

test: test.o $(LIBS) sub.o sub2.o
	$(CC) test.o $(LIBS) -o test

sub.o: sub.c
	$(CC) -c sub.c -o sub.o

sub2.o: sub2.c
	$(CC) -c sub2.c -o sub2.o

$(DL)/libdl.a::
	(cd $(DL); make)

$(DLD)/libdld.a::
	(cd $(DLD); make)

clean::
		-rm -f *.o core [,#@]* *~ *.orig *.old *.bak *.BAK \
			nohup.out Part?? *.ld

clobber::	clean
		-rm -f lib*.a tags TAGS test
