/*
** Definitions of dl library modules.
** Version 1.4, 30-Jul-92.
*/

#include <nlist.h>

typedef void dl_errortype(char *);
typedef void (*dl_funcptr)();

char		*dl_findlibs(char *);
int		 dl_findcache(char *, int, char **);
int		 dl_gettime(char *);
char		*dl_getbinaryname(char *);
char		*dl_expand_script_binary(char *);
int		 dl_ldnfilep();         /* Actually LDFILE */
int		 dl_ldzfilep();         /* Actually LDFILE */
int		 dl_ldfile(char *);
dl_funcptr	dl_loadmod(char *, char *, char *);
int		 dl_loadmod_mult(char *, char *, struct nlist *);
int		 dl_findproc(char *, char *);
int		 dl_linkfile(char *, char *, char *, char *, int, int, int);
void		 dl_error();		/* Actually char *, ... */
void		 dl_message();		/* Actually char *, ... */
dl_errortype	 dl_defaulterror;
dl_errortype	 dl_defaultmessage;
dl_errortype	 dl_nomessage;
void		 dl_seterror(dl_errortype *);
void		 dl_setmessage(dl_errortype *);
int		 dl_checkrange(long, long);
int		 dl_setrange(long, long);
void		*dl_getrange(long);
int		 dl_hashaddrs(char *, long, long, long *, long *);
