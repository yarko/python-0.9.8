extern char *p;

static int large[100000];

chain () {
    bzero (large, 100000 * sizeof (int));
    printf ("I am chain1\n");
    p[5] = '2';			    /* modify the string holding the next
				       file to be loaded. */
}
