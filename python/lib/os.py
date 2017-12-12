# os.py -- either mac or posix depending on what system we're on.

# This exports:
# - all functions from either posix or mac, e.g., os.unlink, os.stat, etc.
# - os.path is either module posixpath or macpath
# - os.name is either 'posix' or 'mac'
# - os.curdir is a string representing the current directory ('.' or ':')
# - os.pardir is a string representing the parent directory ('..' or '::')
# - os.sep is the (or a most common) pathname separator ('/' or ':')

# Programs that import and use 'os' stand a better chance of being
# portable between different platforms.  Of course, they must then
# only use functions that are defined by all platforms (e.g., unlink
# and opendir), and leave all pathname manipulation to os.path
# (e.g., split and join).

# XXX This will need to distinguish between real posix and MS-DOS emulation

try:
	from posix import *
	from posix import _exit
	name = 'posix'
	curdir = '.'
	pardir = '..'
	sep = '/'
	import posixpath
	path = posixpath
	del posixpath
except ImportError:
	from mac import *
	name = 'mac'
	curdir = ':'
	pardir = '::'
	sep = ':'
	import macpath
	path = macpath
	del macpath
