# Conversion pipeline templates
# =============================


# The problem:
# ------------
# 
# Suppose you have some data that you want to convert to another format
# (e.g. from GIF image format to PPM image format).  Maybe the
# conversion involves several steps (e.g. piping it through compress or
# uuencode).  Some of the conversion steps may require that their input
# is a disk file, others may be able to read standard input; similar for
# their output.  The input to the entire conversion may also be read
# from a disk file or from an open file, and similar for its output.
# 
# The module lets you construct a pipeline template by sticking one or
# more conversion steps together.  It will take care of creating and
# removing temporary files if they are necessary to hold intermediate
# data.  You can then use the template to do conversions from many
# different sources to many different destinations.  The temporary
# file names used are different each time the template is used.
#
# The templates are objects so you can create templates for many
# different conversion steps and store them in a dictionary, for
# instance.


# Directions:
# -----------
#
# To create a template:
#   t = Template().init()
#
# To add a conversion step to a template:
#   t.append(command, kind)
# where kind is a string of two characters: the first is '-' if the
# command reads its standard input or 'f' if it requires a file; the
# second likewise for the output. The command must be valid /bin/sh
# syntax.  If input or output files are required, they are passed as
# $IN and $OUT; otherwise, it must be  possible to use the command in
# a pipeline.
#
# To add a conversion step at the beginning:
#   t.prepend(command, kind)
#
# To convert a file to another file using a template:
#   sts = t.copy(infile, outfile)
# If infile or outfile are the empty string, standard input is read or
# standard output is written, respectively.  The return value is the
# exit status of the conversion pipeline.
# 
# To open a file for reading or writing through a conversion pipeline:
#   fp = t.open(file, mode)
# where mode is 'r' to read the file, or 'w' to write it -- just like
# for the built-in function open() or for os.popen().
#
# To create a new template object initialized to a given one:
#   t2 = t.clone()
#
# For an example, see the function test() at the end of the file.


import sys
import regex

import os
import tempfile
import string


# Conversion step kinds

FILEIN_FILEOUT = 'ff'			# Must read & write real files
STDIN_FILEOUT  = '-f'			# Must write a real file
FILEIN_STDOUT  = 'f-'			# Must read a real file
STDIN_STDOUT   = '--'			# Normal pipeline element
SOURCE         = '.-'			# Must be first, writes stdout
SINK           = '-.'			# Must be last, reads stdin

stepkinds = [FILEIN_FILEOUT, STDIN_FILEOUT, FILEIN_STDOUT, STDIN_STDOUT, \
	     SOURCE, SINK]


# A pipeline template is a Template object:

class Template:

	# Template().init() returns a fresh pipeline template
	def init(self):
		self.debugging = 0
		self.reset()
		return self

	# t.__repr__() implements `t`
	def __repr__(self):
		return '<Template instance, steps=' + `self.steps` + '>'

	# t.reset() restores a pipeline template to its initial state
	def reset(self):
		self.steps = []

	# t.clone() returns a new pipeline template with identical
	# initial state as the current one
	def clone(self):
		t = Template().init()
		t.steps = self.steps[:]
		t.debugging = self.debugging
		return t

	# t.debug(flag) turns debugging on or off
	def debug(self, flag):
		self.debugging = flag

	# t.append(cmd, kind) adds a new step at the end
	def append(self, cmd, kind):
		if type(cmd) <> type(''):
			raise TypeError, \
			      'Template.append: cmd must be a string'
		if kind not in stepkinds:
			raise ValueError, \
			      'Template.append: bad kind ' + `kind`
		if kind == SOURCE:
			raise ValueError, \
			      'Template.append: SOURCE can only be prepended'
		if self.steps <> [] and self.steps[-1][1] == SINK:
			raise ValueError, \
			      'Template.append: already ends with SINK'
		if kind[0] == 'f' and regex.search('\$IN', cmd) < 0:
			raise ValueError, \
			      'Template.append: missing $IN in cmd'
		if kind[1] == 'f' and regex.search('\$OUT', cmd) < 0:
			raise ValueError, \
			      'Template.append: missing $OUT in cmd'
		self.steps.append((cmd, kind))

	# t.prepend(cmd, kind) adds a new step at the front
	def prepend(self, cmd, kind):
		if type(cmd) <> type(''):
			raise TypeError, \
			      'Template.prepend: cmd must be a string'
		if kind not in stepkinds:
			raise ValueError, \
			      'Template.prepend: bad kind ' + `kind`
		if kind == SINK:
			raise ValueError, \
			      'Template.prepend: SINK can only be appended'
		if self.steps <> [] and self.steps[0][1] == SOURCE:
			raise ValueError, \
			      'Template.prepend: already begins with SOURCE'
		if kind[0] == 'f' and regex.search('\$IN\>', cmd) < 0:
			raise ValueError, \
			      'Template.prepend: missing $IN in cmd'
		if kind[1] == 'f' and regex.search('\$OUT\>', cmd) < 0:
			raise ValueError, \
			      'Template.prepend: missing $OUT in cmd'
		self.steps.insert(0, (cmd, kind))

	# t.open(file, rw) returns a pipe or file object open for
	# reading or writing; the file is the other end of the pipeline
	def open(self, file, rw):
		if rw == 'r':
			return self.open_r(file)
		if rw == 'w':
			return self.open_w(file)
		raise ValueError, \
		      'Template.open: rw must be \'r\' or \'w\', not ' + `rw`

	# t.open_r(file) and t.open_w(file) implement
	# t.open(file, 'r') and t.open(file, 'w') respectively

	def open_r(self, file):
		if self.steps == []:
			return open(file, 'r')
		if self.steps[-1][1] == SINK:
			raise ValueError, \
			      'Template.open_r: pipeline ends width SINK'
		cmd = self.makepipeline(file, '')
		return os.popen(cmd, 'r')

	def open_w(self, file):
		if self.steps == []:
			return open(file, 'w')
		if self.steps[0][1] == SOURCE:
			raise ValueError, \
			      'Template.open_w: pipeline begins with SOURCE'
		cmd = self.makepipeline('', file)
		return os.popen(cmd, 'w')

	def copy(self, infile, outfile):
		return os.system(self.makepipeline(infile, outfile))

	def makepipeline(self, infile, outfile):
		cmd = makepipeline(infile, self.steps, outfile)
		if self.debugging:
			print cmd
			cmd = 'set -x; ' + cmd
		return cmd


def makepipeline(infile, steps, outfile):
	# Build a list with for each command:
	# [input filename or '', command string, kind, output filename or '']
	
	list = []
	for cmd, kind in steps:
		list.append(['', cmd, kind, ''])
	#
	# Make sure there is at least one step
	#
	if list == []:
		list.append(['', 'cat', '--', ''])
	#
	# Take care of the input and output ends
	#
	[cmd, kind] = list[0][1:3]
	if kind[0] == 'f' and not infile:
		list.insert(0, ['', 'cat', '--', ''])
	list[0][0] = infile
	#
	[cmd, kind] = list[-1][1:3]
	if kind[1] == 'f' and not outfile:
		list.append(['', 'cat', '--', ''])
	list[-1][-1] = outfile
	#
	# Invent temporary files to connect stages that need files
	#
	garbage = []
	for i in range(1, len(list)):
		lkind = list[i-1][2]
		rkind = list[i][2]
		if lkind[1] == 'f' or rkind[0] == 'f':
			temp = tempfile.mktemp()
			garbage.append(temp)
			list[i-1][-1] = list[i][0] = temp
	#
	for item in list:
		[inf, cmd, kind, outf] = item
		if kind[1] == 'f':
			cmd = 'OUT=' + quote(outf) + '; ' + cmd
		if kind[0] == 'f':
			cmd = 'IN=' + quote(inf) + '; ' + cmd
		if kind[0] == '-' and inf:
			cmd = cmd + ' <' + quote(inf)
		if kind[1] == '-' and outf:
			cmd = cmd + ' >' + quote(outf)
		item[1] = cmd
	#
	cmdlist = list[0][1]
	for item in list[1:]:
		[cmd, kind] = item[1:3]
		if item[0] == '':
			if 'f' in kind:
				cmd = '{ ' + cmd + '; }'
			cmdlist = cmdlist + ' |\n' + cmd
		else:
			cmdlist = cmdlist + '\n' + cmd
	#
	if garbage:
		rmcmd = 'rm -f'
		for file in garbage:
			rmcmd = rmcmd + ' ' + quote(file)
		trapcmd = 'trap ' + quote(rmcmd + '; exit') + ' 1 2 3 13 14 15'
		cmdlist = trapcmd + '\n' + cmdlist + '\n' + rmcmd
	#
	return cmdlist


# Reliably quote a string as a single argument for /bin/sh

_safechars = string.letters + string.digits + '!@%_-+=:,./'	# Safe unquoted
_funnychars = '"`$\\'				# Unsafe inside "double quotes"

def quote(file):
	for c in file:
		if c not in _safechars:
			break
	else:
		return file
	if '\'' not in file:
		return '\'' + file + '\''
	res = ''
	for c in file:
		if c in _funnychars:
			c = '\\' + c
		res = res + c
	return '"' + res + '"'


# Small test program and example

def test():
	import os
	print 'Testing...'
	t = Template().init()
	t.append('togif $IN $OUT', 'ff')
	t.append('giftoppm', '--')
	t.append('ppmtogif >$OUT', '-f')
	t.append('fromgif $IN $OUT', 'ff')
	t.debug(1)
	FILE = '/usr/local/images/rgb/rogues/guido.rgb'
	t.copy(FILE, '@temp')
	print 'Done.'
