#include "dld.h"

/* Example to unlink the "main" module (the current executable) so that
   another "main" can be linked in and executed.

   To execute, type "reload reload-test".
 */
    
main (argc, argv)
int argc;
char *argv[];
{

    register void (*func) () ;
    int *new_brk;
    
    (void) dld_init(argv[0]);

    /* unlink itself */
    dld_unlink_by_file (argv[0], 1);

    dld_link (argv[1]);
#if defined(sequent)
    func = (void (*)()) dld_get_func ("main");
    (*func) ();
#else
    if (dld_function_executable_p ("main")) {
	func = (void (*)()) dld_get_func ("main");

	/* "curbrk" is a symbol used by sbrk(2) to record the current
	   break of the process.  It is initialized to the address of
	   "_end". Since we are loading in a new copy of sbrk, we must
	   set its value to the true current break of the process.
	   Otherwise, the first call to the new sbrk will get a seg. fault */
	if (new_brk = (int *) dld_get_bare_symbol ("curbrk")) {
	    *new_brk = sbrk(0);
	    (*func) ();
	}
    }
#endif
}
