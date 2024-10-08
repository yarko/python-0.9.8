# Convert "arbitrary" sound files to AIFF files (Apple and SGI's audio format).
# Input may be compressed.
# Uncompressed file type may be AIFF, WAV, VOC, 8SVX, NeXT/Sun, and others.
# An exception is raised if the file is not of a recognized type.
# Returned filename is either the input filename or a temporary filename;
# in the latter case the caller must ensure that it is removed.
# Other temporary files used are removed by the function.

import os
import tempfile
import pipes
import sndhdr

table = {}

t = pipes.Template().init()
t.append('sox -t au - -t aiff -r 8000 -', '--')
table['au'] = t

# XXX The following is actually sub-optimal.
# XXX The HCOM sampling rate can be 22k, 22k/2, 22k/3 or 22k/4.
# XXX We must force the output sampling rate else the SGI won't play
# XXX files sampled at 5.5k or 7.333k; however this means that files
# XXX sampled at 11k are unnecessarily expanded.
# XXX Similar comments apply to some other file types.
t = pipes.Template().init()
t.append('sox -t hcom - -t aiff -r 22050 -', '--')
table['hcom'] = t

t = pipes.Template().init()
t.append('sox -t voc - -t aiff -r 11025 -', '--')
table['voc'] = t

t = pipes.Template().init()
t.append('sox -t wav - -t aiff -', '--')
table['wav'] = t

t = pipes.Template().init()
t.append('sox -t 8svx - -t aiff -r 16000 -', '--')
table['8svx'] = t

t = pipes.Template().init()
t.append('sox -t sndt - -t aiff -r 16000 -', '--')
table['sndt'] = t

t = pipes.Template().init()
t.append('sox -t sndr - -t aiff -r 16000 -', '--')
table['sndr'] = t

uncompress = pipes.Template().init()
uncompress.append('uncompress', '--')


error = 'toaiff.error' # Exception

def toaiff(filename):
	temps = []
	ret = None
	try:
		ret = _toaiff(filename, temps)
	finally:
		for temp in temps[:]:
			if temp <> ret:
				try:
					os.unlink(temp)
				except os.error:
					pass
				temps.remove(temp)
	return ret

def _toaiff(filename, temps):
	if filename[-2:] == '.Z':
		fname = tempfile.mktemp()
		temps.append(fname)
		sts = uncompress.copy(filename, fname)
		if sts:
			raise error, filename + ': uncomress failed'
	else:
		fname = filename
	try:
		ftype = sndhdr.whathdr(fname)
		if ftype:
			ftype = ftype[0] # All we're interested in
	except IOError:
		if type(msg) == type(()) and len(msg) == 2 and \
			type(msg[0]) == type(0) and type(msg[1]) == type(''):
			msg = msg[1]
		if type(msg) <> type(''):
			msg = `msg`
		raise error, filename + ': ' + msg
	if ftype == 'aiff':
		return fname
	if ftype == None or not table.has_key(ftype):
		raise error, \
			filename + ': unsupported audio file type ' + `ftype`
	temp = tempfile.mktemp()
	temps.append(temp)
	sts = table[ftype].copy(fname, temp)
	if sts:
		raise error, filename + ': conversion to aiff failed'
	return temp
