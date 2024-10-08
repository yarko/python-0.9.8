#! /ufs/guido/bin/sgi/python
#! /usr/local/bin/python
# Check that all ".pyc" files exist and are up-to-date
# Uses module 'os'

import sys
import os
from stat import ST_MTIME

def main():
	silent = 0
	verbose = 0
	if sys.argv[1:]:
		if sys.argv[1] == '-v':
			verbose = 1
		elif sys.argv[1] == '-s':
			silent = 1
	MAGIC = '\0\0\0\0'
	try:
		if sys.version[:5] >= '0.9.4':
			MAGIC = '\224\224\224\0'
	except:
		pass
	if not silent:
		print 'Using MAGIC word', `MAGIC`
	for dirname in sys.path:
		try:
			names = os.listdir(dirname)
		except os.error:
			print 'Cannot list directory', `dirname`
			continue
		if not silent:
			print 'Checking', `dirname`, '...'
		names.sort()
		for name in names:
			if name[-3:] == '.py':
				name = os.path.join(dirname, name)
				try:
					st = os.stat(name)
				except os.error:
					print 'Cannot stat', `name`
					continue
				if verbose:
					print 'Check', `name`, '...'
				name_c = name + 'c'
				try:
					f = open(name_c, 'r')
				except IOError:
					print 'Cannot open', `name_c`
					continue
				magic_str = f.read(4)
				mtime_str = f.read(4)
				f.close()
				if magic_str <> MAGIC:
					print 'Bad MAGIC word in ".pyc" file',
					print `name_c`
					continue
				mtime = get_long(mtime_str)
				if mtime == 0 or mtime == -1:
					print 'Bad ".pyc" file', `name_c`
				elif mtime <> st[ST_MTIME]:
					print 'Out-of-date ".pyc" file',
					print `name_c`

def get_long(s):
	if len(s) <> 4:
		return -1
	return ord(s[0]) + (ord(s[1])<<8) + (ord(s[2])<<16) + (ord(s[3])<<24)

main()
