test_remove (argc, argv)
int argc;
char *argv[];
{
    register int i;

    for (i = 1; i < argc; i++) 
	dld_remove_defined_symbol (argv[i]);
}
