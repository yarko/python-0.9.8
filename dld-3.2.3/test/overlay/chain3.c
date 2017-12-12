extern char *p;

int large[100000];

chain () {
    bzero (large, 100000 * sizeof (int));
    printf ("I am chain3\n");
    p = 0;
}
