#include <dld.h>
#include <a.out.h>    

test_define ()
{
    int *i;
    
    dld_link ("print_global.o");
    dld_define_sym ("global_int", sizeof(int));
    i = (int *) dld_get_symbol ("global_int");
    *i = 12345;
    printf ("print_global should now give 12345\n");
}
    
    
	    
    
