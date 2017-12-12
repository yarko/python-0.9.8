/* print out all the undefined symbols */

#include <dld.h>

list_undefined () {
    char **list = dld_list_undefined_sym ();

    if (list) {
	register int i;
	    
	printf ("There are a total of %d undefined symbols:\n",
		dld_undefined_sym_count);
	for (i = 0; i < dld_undefined_sym_count; i++)
	    printf ("%d: %s\n", i+1, list[i]);
    } else
	printf ("No undefined symbols\n");
}
    
