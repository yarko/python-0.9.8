/*
** Test.c - Test shared library
*/
#include <stdio.h>

#include "dl.h"

main(argc, argv)
    int argc;
    char **argv;
{
    dl_funcptr sub1, sub2;
    
    printf("main: load function %s from %s\n", argv[2], argv[1]);
    sub1 = dl_loadmod(argv[0], argv[1], argv[2]);
    if ( sub1 == 0 ) {
	exit(1);
    }
    printf("main: %s is at address 0x%x\n", argv[2], sub1);
    if ( argc == 5 ) {
	 printf("main: load function %s from %s\n", argv[4], argv[3]);
	 sub2 = dl_loadmod(argv[0], argv[3], argv[4]);
	 if ( sub2 == 0 ) {
	     exit(1);
         }
	 printf("main: %s is at address 0x%x\n", argv[4], sub2);
    }
    printf("main: Ca2lling %s\n", argv[2]);
    (*sub1)();
    if ( argc == 5 ) {
	printf("main: calling %s\n", argv[4]);
	(*sub2)();
    }
    printf("main: all done\n");
}

submain() {
    printf("submain: called\n");
}
