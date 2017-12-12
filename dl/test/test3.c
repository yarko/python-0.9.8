/*
** Test.c - Test shared library
*/
#include <stdio.h>

#include "dl.h"

struct nlist wtd[] = {
{"sub1"},
{"sub2"},
{0}
};

main(argc, argv)
    int argc;
    char **argv;
{
    dl_funcptr sub1, sub2, sub3;
    int n;
    
    printf("main: load functions sub1,sub2 from test3sub1.o\n");
    dl_setincr(argv[0]);
    n = dl_loadmod_mult(0, "test3sub1.o", wtd);
    if ( n != 2 ) {
	fprintf(stderr, "Could not find both subroutines\n");
	exit(1);
    }
    sub1 = (dl_funcptr)wtd[0].n_value;
    sub2 = (dl_funcptr)wtd[1].n_value;
    
    sub3 = dl_loadmod(0, "test3sub2.o", "sub3");
    printf("Calling sub1:\n");
    (*sub1)();
    printf("Calling sub2:\n");
    (*sub2)();
    printf("Calling sub3:\n");
    (*sub3)();
}
