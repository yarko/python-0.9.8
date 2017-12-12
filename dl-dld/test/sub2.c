
int i;
int j = 2;

sub1() {
    printf("sub2-sub1: called %f\n", 0.456);
}

sub2() {
    printf("sub2-sub2: calling mainsub\n");
    submain();
    printf("sub2-sub2: returning\n");
}
