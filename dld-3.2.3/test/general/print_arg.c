#include <stdio.h>

print_arg (argc, argv)
int argc;
char **argv;
{
    while (argc)
	printf ("%s\n", argv[--argc]);
}
