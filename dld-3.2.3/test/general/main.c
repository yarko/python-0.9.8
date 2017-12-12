#include <stdio.h>
#include <strings.h>
#include "dld.h"
    
int my_argc;
char **my_argv;

/*
 *  Ask for a object file interactively, then link it in.
 *  User can then enter the function name for execution.
 *  See file "script" for sample inputs.
 */
main (argc, argv)
int argc;
char **argv;
{
    char line[80];

    /* required initialization. */
    (void) dld_init (argv[0]);
    
    my_argv = 0;
    printf ("(dld) ");
    while (gets(line) != NULL) {
	printf ("%s\n", line);
	if (my_argv) free (my_argv);
	parse (line);
	execute (my_argc, my_argv);
	printf ("(dld) ");
    }
}

/* parse the user input.  Split the arguments into my_argv and put number
   of arguments in my_argc, in the same way as the shell parse the command
   line arguments. */
parse (line)
char line[];
{
    register char *p;

    my_argc = 0;
    p = line;
    while (*p) {
	while (*p == '\t' || *p == ' ') p++;
	if (!(*p)) break;
	while (*p != '\t' && *p != ' ' && *p != 0) p++;
	my_argc++;
	if (*p) p++;
    }

    my_argv = (char **) malloc ((my_argc+1) * sizeof (char **));
    
    {
	register int i;
	p = line;
	for (i=0; i<my_argc; i++) {
	    while (*p == '\t' || *p == ' ') p++;
	    my_argv[i] = p;
	    while (*p != '\t' && *p != ' ' && *p != 0) p++;
	    *p = 0;
	    p++;
	}
	my_argv[my_argc] = 0;
    }
} /* parse */

/*
 *  Carry out the user command:
 *  dld object_file.o			-- dynamically link in that file.
 *  ul object_file.o			-- unlink that file.
 *  function_name arg1 arg2 ...		-- execute that function.
 */
execute (my_argc, my_argv)
int my_argc;
char **my_argv;
{
    register int (*func) ();
    
    if (!my_argc) return;
    if (strcmp (my_argv[0], "dld") == 0)
	while (--my_argc) {
	    register int dld_errno;
	    extern char *dld_errmesg;

	    if (dld_link (*(++my_argv)))
		dld_perror ("Can't link");
	}
    else if (!strcmp (my_argv[0], "ul"))
	dld_unlink_by_file (my_argv[1], my_argc >= 3 ? 1 : 0);
    else if (!strcmp (my_argv[0], "uls"))
	dld_unlink_by_symbol (my_argv[1], my_argc >= 3 ? 1 : 0);
    else {
	func = (int (*) ()) dld_get_func (my_argv[0]);
	if (func) {
	    register int i;
	    if (dld_function_executable_p (my_argv[0])) {
		i = (*func) (my_argc, my_argv);
		if (i) printf ("%d\n", i);
	    } else
		printf ("Function %s not executable!\n", my_argv[0]);
	}
	else printf ("illegal command\n");
    }
}
