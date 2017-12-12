/*
** dl_remove_symbol - Zap the given symbol from the string table from an
** a.out file.
**
** Written by Caspar Dik.
*/

#include <stdio.h>
#include <a.out.h>
#include <unistd.h>
#include <fcntl.h>


dl_remsym(char *file, char *symbol)
{
    struct aouthdr aout;
    struct filehdr fhdr;
    HDRR symhdr;
    FILE *bin = fopen(file, "r+");
    int c,i;
    int len;

    if (bin == 0) {
	perror(file);
	return -1;
    }
    len = strlen(symbol) + 1;
    if (fread((char *) &fhdr, sizeof(fhdr), 1, bin) != 1) {
	fclose(bin);
	return -1;
    }
    if (fread((char *) &aout, sizeof(aout), 1, bin) != 1) {
	fclose(bin);
	return -1;
    }
    fseek(bin, fhdr.f_symptr, SEEK_SET);
    if (fread((char *) &symhdr, sizeof(symhdr), 1, bin) != 1)  {
	fclose(bin);
	return -1;
    }
    fseek(bin,symhdr.cbSsExtOffset, SEEK_SET);
    i = 0;
    while ((c = getc(bin)) != -1 && (c != 0 || i != 0)) {
	if (c == symbol[i++]) {
	    if (i == len) {
		fseek(bin, -len, SEEK_CUR);
		for (i = 1; i < len ; i++)
		    putc(1, bin);
		break;
	    }
	} else {
	    i = 0;
	    while ((c = getc(bin)) != -1 && c != 0)
		;
	}
    }
    fclose(bin);
    return(0);
}
