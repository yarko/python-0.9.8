#! /bin/sh

# Shell script to patch Makefile and config.c to support a new optional
# built-in module.  It save the old Makefile and config.c (if it decides
# to change them) as Makefile.old and config.c.old, respectively.
#
#			*** Warning ***
#
# Use at own your risk.  Check the effect.
# This script isn't perfect: it does not fill in libraries or
# meaningful group comments, nor does it know about dependencies
# between modules or architecture dependencies. 
# However, it does the boring work of inserting new lines in all the
# right places in the Makefile and in config.c so you can concentrate
# on more creative work.

case $# in
1)	MOD=$1;;
*)	echo "usage: $0 modulename" 1>&2; exit 2;;
esac

UCMOD=`echo $MOD | tr [a-z] [A-Z] `
EQMOD=`echo $MOD | sed 's/./=/g' `
INIT=init${MOD}
BASE=${MOD}module
FILE=$BASE.c

if test ! -f $FILE
then
	echo "There is no file named $FILE" 1>&2; exit 1
fi

if grep "$INIT" >/dev/null $FILE
then
	:
else
	echo "$FILE does not define $INIT" 1>&2; exit 1
fi

if grep "$BASE" >/dev/null Makefile
then
	echo "Warning: Makefile already references $BASE -- not edited" 1>&2
else
	echo Editing Makefile...
	sed -e '
	/-- ADDMODULE MARKER --/i\
# '$UCMOD' Option\
# '$EQMOD'=======\
#\
##group\
# This enables the '$MOD' module.\
##ifyes Do you want to configure the '$UCMOD' option ? [no]\
#'$UCMOD'_USE=	-DUSE_'$UCMOD'\
#'$UCMOD'_SRC=	'$FILE'\
#'$UCMOD'_OBJ=	'$BASE'.o\
#'$UCMOD'_LIBS=\
#'$UCMOD'_LIBDEPS=\
##endif\
##endg\
\

	/^CONFIGDEFS=/a\
		$('$UCMOD'_USE) \\
	/^LIBDEPS=/a\
		$('$UCMOD'_LIBDEPS) \\
	/^LIBS=/a\
		$('$UCMOD'_LIBS) \\
	/^LIBOBJECTS=/a\
		$('$UCMOD'_OBJ) \\
	/^LIBSOURCES=/a\
		$('$UCMOD'_SRC) \\
	' Makefile >@Makefile || exit
	mv Makefile Makefile.old || exit
	mv @Makefile Makefile || exit
fi

if grep "$INIT" >/dev/null config.c
then
	echo "Warning: config.c already references $INIT -- not edited" 1>&2
else
	echo Editing config.c...
	sed -e '
	/-- ADDMODULE MARKER 1 --/i\
#ifdef USE_'$UCMOD'\
extern void '$INIT'();\
#endif
	/-- ADDMODULE MARKER 2 --/i\
#ifdef USE_'$UCMOD'\
       {"'$MOD'", '$INIT'},\
#endif\

	' config.c >@config.c || exit
	mv config.c config.c.old || exit
	mv @config.c config.c || exit
fi
