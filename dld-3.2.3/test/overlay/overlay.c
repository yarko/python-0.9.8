#include <stdio.h>
#include <sys/time.h>
#include <sys/resource.h>
#include "dld.h"

/* strings to hold the next object file to be linked.  On invocation, the
   linked-in function will modify this string so that a different file will
   be loaded next time. */
char *p = "chain1.o";

/*
 *  To show how different modules can be overlayed onto the same memory
 *  sections.
 */
main (argc, argv)
int argc;
char *argv[];
{
    struct rusage rusage;

    (void) dld_init (argv[0]);

    /* Use the max. memory allocation to show that all the dynamically
       linked in modules indeed share the (more or less) same memory
       sections.  Each module contains a large static array.  If they are
       not overlayed, the max. RSS will increase. */
    
    getrusage (RUSAGE_SELF, &rusage);
    printf ("MAX_RSS = %d page.\n", rusage.ru_maxrss);

    do {
	register void (* func) ();
	register int dld_errno;
	
	printf ("Linking %s\n", p);
	if (dld_errno = dld_link (p)) {
	    fprintf (stderr, "Error linking %s -- code = %d\n", p, dld_errno);
	    exit ();
	}

	getrusage (RUSAGE_SELF, &rusage);
	printf ("MAX_RSS = %d page.\n", rusage.ru_maxrss);
	if (dld_function_executable_p("chain")) {
	    func = (void (*) ()) dld_get_func ("chain");
	    (* func) ();
	}
	dld_unlink_by_symbol ("chain", 0);
    } while (p);
}
