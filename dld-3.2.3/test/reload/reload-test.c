#if defined(sequent)
asm (".comm _387_flt,4");
#endif

int end;			    /* required by sbrk() */

main () {

    printf ("Hello world! -- from reload-test\n");
}
