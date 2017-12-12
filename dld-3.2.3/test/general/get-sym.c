/* print the address and value of the specified symbols */

get_symbol (argc, argv)
int argc;
char *argv[];
{
    register int *value;
    register int i;

    for (i=1; i < argc; i++) {
	value = (int *) dld_get_symbol (argv[i]);
	printf ("%d: address = 0x%x, value = 0x%x\n", i, value, *value);
    }
}
    
