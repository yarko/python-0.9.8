/* explicity reference the given symbol, so that the library routine
   defining this symbol will be loaded */

#include <stdio.h>

need (argc, argv)
int argc;
char *argv[];
{
    register int i;

    for (i = 1; i < argc; i++) {
	register int dld_errno;
	
	printf ("%d: %s", i, argv[i]);
	fflush (stdout);
	if (dld_errno = dld_create_reference (argv[i]))
	    printf ("--Error: %d\n", dld_errno);
	else {
	    if (dld_get_symbol (argv[i]))
		printf ("--Symbol already defined\n");
	    else printf ("\n");
	}
    }
}
