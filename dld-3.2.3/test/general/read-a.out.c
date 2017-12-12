#include <stdio.h>
#include <a.out.h>

#if defined(sun) && defined(sparc)
#define relocation_info reloc_info_sparc
#endif
    
read_a_out (argc, argv)
int argc;
char **argv;
{
    struct exec header;
    struct relocation_info relo;
    struct nlist name_list;
    FILE *objfile;
    char *string;
    int str_size;
    int i;

    if (argc < 1) exit ();

    if ((objfile = fopen (argv[1], "r")) == NULL) {
	perror ("Can't open object file");
	exit ();
    }

    if (!fread (&header, sizeof(header), 1, objfile)) {
	perror ("Can't read header");
	exit ();
    }

    printf ("Header information:\nmagic = 0%o, text size = %d, data size = %d\n",
	    header.a_magic, header.a_text, header.a_data);
    printf ("bss size = %d, syms size = %d, entry point = 0x%x, trsize = %d, drsize = %d\n",
	    header.a_bss, header.a_syms, header.a_entry, header.a_trsize,
	    header.a_drsize);

    
    fseek (objfile, header.a_text + header.a_data + header.a_bss, 1);
    if (header.a_trsize != 0) {
	printf ("\n\nText relocation info\n");
	for (i=0; i<(header.a_trsize/sizeof(relo)); i++) {
	    fread (&relo, sizeof(relo), 1, objfile);

#if defined(sun) && defined(sparc)
	    printf ("Address = 0x%x, local offset = %d\n",
		    relo.r_address, relo.r_index);
	    printf ("extern = %d, relocation type = %d, addend = %d\n",
		    relo.r_extern, relo.r_type, relo.r_addend);
#else
	    
	    printf ("Address = 0x%x, local offset = %d\n",
		    relo.r_address, relo.r_symbolnum);
	    printf ("pc relocated = %d, length = %d, extern = %d\n",
		    relo.r_pcrel, relo.r_length, relo.r_extern);
#endif	    
	}
    }

    if (header.a_drsize != 0) {
	printf ("\n\nData relocation info\n");
	for (i=0; i<(header.a_trsize/sizeof(relo)); i++) {
	    fread (&relo, sizeof(relo), 1, objfile);

#if defined(sun) && defined(sparc)
	    printf ("Address = 0x%x, local offset = %d\n",
		    relo.r_address, relo.r_index);
	    printf ("extern = %d, relocation type = %d, addend = %d\n",
		    relo.r_extern, relo.r_type, relo.r_addend);
#else
	    
	    printf ("Address = 0x%x, local offset = %d\n",
		    relo.r_address, relo.r_symbolnum);
	    printf ("pc relocated = %d, length = %d, extern = %d\n",
		    relo.r_pcrel, relo.r_length, relo.r_extern);
#endif	    
	}
    }

    fseek (objfile, N_STROFF(header), 0);
    fread (&str_size, sizeof(str_size), 1, objfile);
    string = (char *) malloc (str_size);
    fseek (objfile, N_STROFF(header), 0);
    fread (string, 1, str_size, objfile);

    fseek (objfile, N_SYMOFF(header), 0);

    printf ("\n\n");
    for (i=0; i<(header.a_syms/sizeof(struct nlist)); i++) {
	fread (&name_list, sizeof (struct nlist), 1, objfile);
	printf ("string = %s\n", string + name_list.n_un.n_strx);
	printf ("Type = 0x%x, value = 0x%08x\n", name_list.n_type, (int)name_list.n_value);
    }
} 
