Building Python
---------------

Python is portable to a large number of platforms.  The Makefile in
the src directory is used for all UNIX platforms.  For the PC and Mac
ports, see the files BUILD-PC and BUILD-MAC.  The rest of the file
you're reading now is specific to UNIX.

Python can be linked with many optional built-in modules that greatly
enhance its usefullness.  Some optional modules are specific to a
certain platform (in particular there are many modules specific for
SGI machines), and others require the availability of other, freely
available software packages such as the GNU readline library or my own
STDWIN library.

Most of these options can be turned off or on by commenting out or
uncommenting a couple of lines in the Makefile, and possibly editing
one or two of the uncommented lines.  However, since there are many
options, a script has been provided to make the selection of options
easier.  Naturally, the script (Configure.py) is written in Python!
It works by scanning the Makefile for directives such as ##if and
##endif and evey now and then it displays a message and askes you a
question.  The Makefile that is written back still contains the
directives, and disabled lines are not removed but just commented out,
so you can run the script as often as you want, changing your mind or
iteratively arriving at the correct set of options.  Whenever you are
asked a question, the default answer is that currently in effect in
the Makefile.  (Type ? to get some help; enter an EOF to get the
default for the rest of the questions.)

There's of course a chicken-and-egg problem: you need to run the
Configure.py script in order to build a Python interpreter, but you
need to have a working Python interpreter in order to run the script!
Luckily, the script doesn't use any of the fancy optional modules.
The Makefile comes pre-configured with all options turned off, and one
or two manual changes to the Makefile are usually sufficient to build
a minimal Python interpreter.

To be precise, the only change that you normally need to make to the
Makefile is to select the proper setting for the System V flag.  You
do this by editing the Makefile, searching for a line containing the
string "SYSVDEF=", and uncommenting it if your UNIX system is System V
(or a derivative, such as SGI Irix or HP-UX) or leaving it commented
out if your UNIX system is a BSD derivative (such as SunOS 4.x or
Ultrix).

In fact, you don't even need to edit the Makefile -- you can simply
type "make SYSVDEF=-DSYSV" to the shell.  Also note that this flag is
in fact only used to build the file posixmodule.o, and if you've
selected the wrong value for the flag, Make will only fail when it is
building that file.  You don't need to remove any of the .o files
alredy built, you can just change the value of the flag and restart
Make.

If may be possible that you run into more trouble at the link phase,
usually complaints about missing functions (e.g. strtod or getcwd) or
sometimes duplicate definitions.  In that case you may have to edit
the Makefile and change the settings of some options that guide the
use and definition of such functions.  Usually searching for the name
of the missing or duplicate function will send you to an option in the
Makefile that explains what to do.  (If you are working with a really
outlandish version of UNIX, you may have to consult the C sources and
temporarily edit out certain references -- be sure you know what you
are doing!)

Once you've got an executable binary called "python", you should check
if it's working.  If you start it, it should print a short welcome
message (including the version and a copyright notice) and a prompt,
the string >>>.  Type something simple first, e.g. 2+2; it should type
the result (4) back and another prompt.  Now type this:

	import testall

This starts a fairly comprehensive test suite.  It should produce
quite some output, ending with a line saying "Passed all tests."
followed by the prompt again.  You can now quit the interpreter by
typing en EOF (Control-D) at it.

Of course, it's possible that things go less smooth than this.  You
may have to use a debugger, you may need to recompile everything with
the -g flag, and you may even pull out some hairs.  There is little
specific advice that I can give if this happens to you, except one
thing: if you get a core dump, before doing anything else, check your
stack size limit (the csh command "limit stacksize" shows this) and if
it is suspiciously small, see if you still get the core dump with a
limit of 100 k or so.

But let's be optimistic and assume you have a working interpreter.
It's a good idea at this point to save a copy of the Makefile and of
the working, but minimal, Python interpeter that you have now, in case
things go wildly wrong later and you would have to start from scratch.

You can now run the Configure.py script as follows:

	./python Configure.py

(If you have built an earlier distribution of Python, especially the
0.9.6 version, you can skip building a minimal interpreter and use the
0.9.6 interpreter to run the Configure.py script instead.  Pre-0.9.6
Python interpreters may cause trouble though, since the operator for
equality testing has changed from '=' to '=='.)

You'll get to answer a large number of questions, after which the
Makefile will be modified according to your answers.  You don't have
to get the answers right the first time, you can always run the script
another time.  When you are satisfied with the new Makefile, you can
start Make again.  You don't need to throw away any of the object
files that you've just built, except that if you turn on the GNU
READLINE option you must remove tokenizer.o, and if you turn on the
THREAD option you must remove all .o files.

Test the newly built interpreter as explained above.

You can install the interpreter and the files belonging to it using
the install target in the Makefile; in practice this may need a little
help or massaging of the Makefile.  Make sure to have a look at the
documentation in the doc subdirectory -- you need LaTeX to print it
(unless you've got the PostScript version that is separately
available).

The next step is to play with Python.  Read the tutorial.  Check out
the programs in the demo subdirectory.  Subscribe the the Python
mailing list.  Optionally, you can become a Python wizard, but I won't
reveal here how to become one :-)

Good luck!


ANSI (Standard C) Compiler warnings
-----------------------------------

If you are using an ANSI (Standard C) compiler, it is likely that your
compiler will spit out many warnings about illegal initialization
types in certain files, e.g. classobject.c.  These are harmess.

The 'initialization type mismatch' messages come from my habit of
declaring struct members as pointers to functions with a (generic)
object pointer argument, and initializing them with functions whose
argument is a pointer to a particular type of object, which I know
will always be the case ar run time.  I should add casts to the
initializations but it's boring work (and the prototypes are all
different so a simple global substitute isn't enough).
