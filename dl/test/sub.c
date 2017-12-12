
sub01() {
    printf("sub1: called %f\n", 0.123);
}

sub02() {
    printf("sub2: calling mainsub\n");
    submain();
    printf("sub2: returngin\n");
}

sub03() {
    double sin();
    
    printf("Sub3: called. Attempt sin(3.1415):\n");
    printf("sin(%f) = %f\n", 3.1415, sin(3.1415));
}
