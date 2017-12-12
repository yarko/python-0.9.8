#! /usr/local/bin/python
# configure.py -- Python script to (re)configure a Makefile.


# Usage
# =====
#
# Usage : python configure.py [-q] [-v] [input [output]]
#
# -q    : quiet (don't show group descriptions)
# -v    : verbose (show all substitutions and directives)
# input : file to edit, default Makefile
# output: file to place the output, default same as input
#
# If the output file is the same as the input file, a temporary file
# named input.new is created and a backup of the input file named
# input.old is made before moving the temporary file to the input
# file.
#
# It is possible to specify - for input or output; then the script
# will read/write stdin/stdout and is usable as a filter.  If the
# input is stdin, user input is read from /dev/tty, if the output is
# stdout, output for the user goes to stderr.  Note that a single -
# implements a filter from stdin to stdout.


# Purpose
# =======
#
# This copies the Makefile to a temporary file, processing certain
# directives in it that enable, disable or edit some sections based
# upon user input and dynamically available information (e.g., system
# architecture).  At the end, Makefile is moved to a backup name
# and the temporary file moved to Makefile.
#
# The process is idempotent: the resulting Makefile contains all
# directives that make it possible to process it again, and the
# defaults for user input are written in the file.


# Directives
# ==========
#
# Directives are lines beginning with '##' immediately followed by a
# keyword.  Valid directives are:
#
# ##if    - Impose a restriction.  The rest of the line is a Python
#           expression that should evaluate to true or false.
#           If false, the lines until a matching ##endif are ignored
#           (but copied, and explicitly disabled when in a group).
#           ##if/##endif blocks can be nested.
#
# ##ifyes, ##ifno
#         - Like ##if but instead of evaluating a Python expression,
#           the user is asked to respond with yes or no.  The rest of
#           the line is the prompt.  If the prompt ends with [yes] or
#           [no], this is taken to be the default.  The line is
#           modified on output to contain the user's response as
#           default.
#
# ##elif  - As expected.
#
# ##elifyes, ##elifno
#         - Combination of ##ifyes/##ifno and ##elif.
#
# ##else  - As expected.
#
# ##endif - End the corresponding ##if block.
#
# ##echo  - Show the rest of the line to the user, even if -q specified.
#
# ##edit, ##editfile, ##editdir
#         - Indicate that the next line is a definition of a Make
#           variable which can be edited by the user (default is no
#           change).  If the directive is ##editfile, the definition
#           must be an existing file name; if it is ##editdir, it must
#           be an existing directory name.  The rest of the directive
#           line contains an optional prompt.  The user input may use
#           ~/ or ~user/ to indicate a home directory.
#
# ##exec  - The rest of the line is a Python statement that is
#           executed in the same environment as ##if conditions.
#
# ##group - Begin a group of lines to be treated specially.
#           Certain lines within a group are modified, see below.
#           Groups can be 'enabled' or 'disabled'.  Unless inside the
#           'false' branch of an ##if, a group is initially enabled.
#           Groups cannot be nested (but they can contain and be
#           contained in ##if directives).
#
# ##endg  - End a group.
#
# Inside a group, some types of lines are treated special:
#
# - Lines beginning with a # followed by a space, tab or newline are
#   part of the description of the group, and are shown to the user
#   unless the group is disabled.  This is ignored if the user has
#   selected 'quiet' mode.
#
# - Lines beginning with a letter or with a # immediately followed by
#   a letter are part of the optional definitions in the group.  If
#   the group is enabled, the # is removed if present; if it is
#   disabled, a # is inserted if not present.  If the group is enabled
#   and the line looks like a variable definition, a string variable
#   with the same name and value is introduced in the Python
#   environment used by ##if and ##exec.
#
# - Directives are executed if the group is enabled.
#
# - All other lines are copied literally.
#
# When the user is asked for input, the following escapes are
# recognized:
#
# - empty input means no change (use the default)
#
# - a single ? displays some help (e.g. repeats the question)
#
# - an EOF avoids asking any more questions, using the default for
#   all subsequent questions.


# Imported modules

import sys
sys.path.insert(0, '../lib')
import os
import string
import getopt


# Command line options

quiet = 0
verbose = 0


# If noask is set, no further questions are asked

noask = 0


# Main program

def main():
	global quiet, verbose
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'qv')
	except getopt.error, msg:
		sys.stderr.write(msg + '\n')
		usage()

	for opt, arg in opts:
		if opt == '-q':
			quiet = 1
			verbose = 0
		elif opt == '-v':
			verbose = 1
			quiet = 0

	if args:
		if len(args) > 2: usage()
		INPUT = args[0]
		if len(args) > 1: OUTPUT = args[1]
		else: OUTPUT = INPUT
	else:
		INPUT = OUTPUT = 'Makefile'

	if INPUT == '-':
		ifp = sys.stdin
		sys.stdin = myopen('/dev/tty', 'r')
	else:
		ifp = myopen(INPUT, 'r')

	TEMP = BACKUP = None
	if OUTPUT == '-':
		ofp = sys.stdout
		sys.stdout = sys.stderr
	elif OUTPUT == INPUT:
		TEMP = OUTPUT + '.new'
		BACKUP = OUTPUT + '.old'
		ofp = myopen(TEMP, 'w')
	else:
		ofp = myopen(OUTPUT, 'w')

	gbls = makeglobals()
	gbls['INPUT'] = INPUT
	gbls['OUTPUT'] = OUTPUT
	gbls['TEMP'] = TEMP
	gbls['BACKUP'] = BACKUP

	try:
		process(ifp, ofp, gbls)
	except KeyboardInterrupt:
		sys.stderr.write('\n[Interrupt]\n')
		if TEMP:
			os.unlink(TEMP)
		sys.exit(1)

	if OUTPUT == '-':
		ofp.flush()
	else:
		ofp.close()
		if TEMP:
			if BACKUP:
				os.rename(OUTPUT, BACKUP)
			os.rename(TEMP, OUTPUT)


# Print usage message and exit(2)

def usage():
	sys.stderr.write( \
		'Usage: python configure.py [-q] [-v] [input [output]]\n')
	sys.stderr.write('-q: quiet (no long explanations)\n')
	sys.stderr.write('-v: verbose (show commands, substitutions etc.)\n')
	sys.stderr.write('Default input: Makefile\n')
	sys.stderr.write('Default output: same as input\n')
	sys.stderr.write('Specifying "-" as input operates as a filter\n')
	sys.exit(2)


# Open a file, on failure print a message and exit(1)

def myopen(file, mode):
	try:
		return open(file, mode)
	except IOError, msg:
		sys.stderr.write( \
			file + ': cannot open (' + mode + '): ' + `msg` + '\n')
		sys.exit(1)


# Various constants used by the parser etc.

IDCHARS = string.letters
YES = 'yes'
NO = 'no'


# Copy lines from ifp to ofp, reading and processing directives

def process(ifp, ofp, gbls):
	skip = 0
	ingroup = 0
	edit = 0
	lineno = 0
	stack = []
	# From last ##edit directive:
	editprompt = ''
	editmode = ''

	while 1:
		line = ifp.readline()
		if not line:
			if stack:
				print '*** Unterminated ##if or ##group'
				sys.exit(1)
			if lineno == 0:
				print '*** Warning: empty input'
			break
		lineno = lineno + 1

		if edit:
			if not (line[0] in IDCHARS or \
				line[0] == '#' and line[1] in IDCHARS):
				print '*** Bad edit target at line', lineno
				print line,
			else:
				if verbose: print line,
				line = editline(editprompt, line, editmode)
				if verbose: print '(after edit):', line,
			edit = 0

		if line[:2] <> '##' or len(line) < 3 or line[3] not in IDCHARS:
			pass # Not really a directive

		elif line[:7] == '##group':
			if ingroup:
				print '*** nested ##group at line', lineno
				print line,
			else:
				if verbose: print line,
				ingroup = 1
				stack.append('##group')
		elif line[:6] == '##endg':
			if not stack or stack[-1] <> '##group':
				print '*** unmatched ##endg at line', lineno
				print line,
			else:
				if verbose: print line,
				ingroup = 0
				if skip == len(stack):
					skip = 0
				del stack[-1]

		elif line[:4] == '##if':
			stack.append('##if')
			if not skip:
				line, result = execif(line, lineno, gbls)
				if result:
					stack[-1] = '##if1'
				else:
					skip = len(stack)
					stack[-1] = '##if0'
		elif line[:6] == '##elif':
			if not stack or stack[-1][:4] <> '##if':
				print '*** unmatched ##elif at line', lineno
				print line,
			else:
				if skip == len(stack) and stack[-1] == '##if0':
					line, result = \
						execif(line, lineno, gbls)
					if result:
						skip = 0
						stack[-1] = '##if1'
				elif skip == 0:
					skip = len(stack)
					if verbose: print line,
		elif line[:6] == '##else':
			if not stack or stack[-1][:4] <> '##if':
				print '*** unmatched ##else at line', lineno
				print line,
			else:
				if skip == len(stack) and stack[-1] == '##if0':
					skip = 0
					if verbose: print line,
				elif skip == 0:
					skip = len(stack)
					if verbose: print line,
				stack[-1] = '##else'
		elif line[:7] == '##endif':
			if not stack or  stack[-1][:4] not in ('##if', '##el'):
				print '*** unmatched ##endif at line', lineno
				print line,
			else:
				if skip == len(stack):
					skip = 0
					if verbose: print line,
				elif skip == 0:
					if verbose: print line,
				del stack[-1]

		elif line[:6] == '##echo':
			if not skip:
				if verbose: print line,
				print string.strip(line[6:])
		elif line[:6] == '##edit':
			if not skip:
				if verbose: print line,
				i = 6
				while line[i] in IDCHARS: i = i+1
				editmode = line[6:i]
				prompt = string.strip(line[i:])
				edit = 1
		elif line[:6] == '##exec':
			if not skip:
				if verbose: print line,
				execstmt(string.strip(line[6:]), gbls)
		else:
			print '*** bad directive at line', lineno,
			print line,

		if ingroup:
			if skip:
				if line[0] in IDCHARS:
					line = '#' + line
					if verbose: print '-->', line,
				elif line[0] == '#' and line[1] in IDCHARS:
					if verbose: print '---', line,
			else:
				if line[0] == '#' and line[1] in IDCHARS:
					line = line[1:]
					if verbose: print '-->', line,
				elif line[0] == '#' and line[1] in ' \t\n':
					if not quiet: print line,
				elif line[0] in IDCHARS:
					if verbose: print '---', line,
				if '=' in line:
					# Make it a string in gbls
					i = string.index(line, '=')
					name = string.strip(line[:i])
					value = string.strip(line[i+1:])
					gbls[name] = value

		ofp.write(line)


# Execute an ##[el]if[yes|no] statement

def execif(line, lineno, gbls):
	if verbose: print line,
	if line[:4] == '##if':
		start = 4
	elif line[:6] == '##elif':
		start = 6
	else:
		raise ValueError, 'execif needs ##if or ##elif'
	i = start
	while line[i] in IDCHARS: i = i+1
	iftype = line[start:i]
	prompt = string.strip(line[i:])
	if not iftype:
		expr = string.strip(line[start:])
		result = evalexpr(expr, gbls)
	elif iftype in (YES, NO):
		default = getdefault(prompt)
		reply = askyesno(prompt, default)
		line = setdefault(line, reply)
		result = (reply == iftype)
	else:
		print '*** bad ##if at line', lineno
		print line,
		result = 0
	return line, result


# Evaluate a boolean

def evalexpr(expr, gbls):
	try:
		return eval(expr, gbls)
	except:
		print '*** Expression', `expr`, 'raised exception (assumed 0)'
		print '***', sys.exc_type, ':', `sys.exc_value`
		return 0


# Execute a statement

def execstmt(stmt, gbls):
	try:
		exec(stmt + '\n', gbls)
	except:
		print '*** Statement', `stmt`, 'raised exception'
		print '***', sys.exc_type, ':', `sys.exc_value`


# Define some constants usable in ##if and ##exec directives.
# The Makefile can add variables using ##exec.

def makeglobals():

	gbls = {}

	# Add some constants

	gbls['true'] = gbls['TRUE'] = 1
	gbls['false'] = gbls['FALSE'] = 0
	gbls['yes'] = gbls['YES'] = YES
	gbls['no'] = gbls['NO'] = NO

	# Add some modules

	gbls['os'] = os
	gbls['string'] = string
	gbls['sys'] = sys

	# Add some functions
	
	gbls['editline'] = editline
	gbls['askyesno'] = askyesno

	return gbls


# Edit a line (for ##edit)

def editline(prompt, line, editmode):
	global noask, quiet
	if noask:
		return line

	if '=' in line:
		i = string.index(line, '=')
		if not prompt:
			name = line[:i]
			if name[0] == '#': name = name[1:]
			name = string.strip(name)
			prompt = 'Enter value for ' + name
		i = i+1
		while i < len(line) and line[i] in ' \t':
			i = i+1
	else:
		i = 0
		if not prompt:
			prompt = 'Enter value'

	default = string.strip(line[i:])
	prompt = prompt + ' [' + default + '] '
	
	while 1:
		try:
			reply = raw_input(prompt)
			if not sys.stdin.isatty():
				print reply
		except EOFError:
			print '[EOF]'
			noask = 1
			if not verbose: quiet = 1
			return line
		reply = string.strip(reply)
		if reply == '':
			reply = default
			# It must still be checked for validity
		elif reply == '?':
			if editmode == 'file':
				print 'Please enter a valid file name.'
			elif editmode == 'dir':
				print 'Please enter a valid directory name.'
			else:
				print 'Please enter a string.'
			if editmode:
				print '~ or ~user are expanded properly.'
			print 'An empty line uses the default:', `default`
			print 'An EOF uses the default now and in the future.'
			continue
		if editmode:
			reply = os.path.expanduser(reply) # Expand ~[user]
			if not os.path.exists(reply):
				print 'Sorry,', `reply`, 'does not exist.'
				print 'Please try again.'
				continue
			if editmode == 'file' and os.path.isdir(reply):
				print 'Sorry,', `reply`, 'is a directory.'
				print 'Please try again.'
				continue
			if editmode == 'dir' and not os.path.isdir(reply):
				print 'Sorry,', `reply`, 'is not a directory.'
				print 'Please try again.'
				continue
		return line[:i] + reply + '\n'


# Extract the default from a prompt

def getdefault(prompt):
	if prompt[-5:] == '[' + YES + ']':
		return YES
	return NO


# Change the default in a line

def setdefault(line, default):
	default = '[' + default + ']'
	if line[-1:] == '\n':
		line = line[:-1]
	if line[-5:] == '[' + YES + ']':
		line = line[:-5] + default
	elif line[-4:] == '[' + NO + ']':
		line = line[:-4] + default
	else:
		line = line + ' ' + default
	return line + '\n'


# Ask a yes/no question

def askyesno(prompt, default):
	global noask, quiet
	if noask:
		return default

	if prompt[-2-len(default):] == '[' + default + ']':
		prompt = string.strip(prompt[:-2-len(default)])
	if not prompt:
		prompt = '(missing question)'
	prompt = prompt + ' [' + default + '] '

	while 1:
		try:
			reply = raw_input(prompt)
			if not sys.stdin.isatty():
				print reply
		except EOFError:
			print '[EOF]'
			noask = 1
			if not verbose: quiet = 1
			return default
		reply = string.lower(string.strip(reply))
		if reply == '':
			return default
		if reply == YES[:len(reply)]:
			return YES
		if reply == NO[:len(reply)]:
			return NO
		if reply == '?':
			print 'Please answer by typing', YES, 'or', NO + '.'
			print 'An empty line uses the default:', default + '.'
			print 'An EOF uses the default now and in the future.'
		else:
			print 'Wrong input (? for help).'


# Now call the main program

main()
