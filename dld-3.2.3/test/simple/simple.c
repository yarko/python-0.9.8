#include "dld.h"
    
main (argc, argv)
int argc;
char *argv[];
{
    void (*func) ();
    
    (void) dld_init (argv[0]);

    printf ("Hello world from %s\n", argv[0]);
    func = (void (*) ()) dld_get_func ("printf");
    (*func) ("Hello world from %s\n", argv[0]);
}
