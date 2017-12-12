
int i;
int j = 2;

sub1() {
    printf("sub1: called %f\n", 0.123);
}

sub2() {
    printf("sub2: calling mainsub\n");
    submain();
    printf("sub2: returngin\n");
}

sub3() {
    double sin();
    
    printf("Sub3: called. Attempt sin(3.1415):\n");
    printf("sin(%f) = %f\n", 3.1415, sin(3.1415));
}
