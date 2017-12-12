
sub21() {
    printf("sub2-sub1: called %f\n", 0.456);
}

sub22() {
    printf("sub2-sub2: calling mainsub\n");
    submain();
    printf("sub2-sub2: returngin\n");
}
