#include "dld.h"
    
int x;

/*
 *  Dynamically link in "add1.o", which defines the function "add1".
 *  Invoke "add1" to increment the global variable "x" defined *here*.
 */
main (argc, argv)
int argc;
char *argv[];
{
    register void (*func) ();

    /* required initialization. */
    (void) dld_init (argv[0]);

    x = 1;
    printf ("global variable x = %d\n", x);

    dld_link ("add1.o");

    /* grap the entry point for function "add1" */
    func = (void (*) ()) dld_get_func ("add1");

    /* invoke "add1" */
    (*func) ();
    printf ("global variable x = %d\n", x);
}
