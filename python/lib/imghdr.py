# Recognizing image files based on their first few bytes.


#-------------------------#
# Recognize sound headers #
#-------------------------#

def what(filename):
	f = open(filename, 'r')
	h = f.read(32)
	for tf in tests:
		res = tf(h, f)
		if res:
			return res
	return None


#---------------------------------#
# Subroutines per image file type #
#---------------------------------#

tests = []

def test_rgb(h, f):
	# SGI image library
	if h[:2] == '\001\332':
		return 'rgb'

tests.append(test_rgb)

def test_gif(h, f):
	# GIF ('87 and '89 variants)
	if h[:6] in ('GIF87a', 'GIF89a'):
		return 'gif'

tests.append(test_gif)

def test_pbm(h, f):
	# PBM (portable bitmap)
	if len(h) >= 3 and \
		h[0] == 'P' and h[1] in '14' and h[2] in ' \t\n\r':
		return 'pbm'

tests.append(test_pbm)

def test_pgm(h, f):
	# PGM (portable graymap)
	if len(h) >= 3 and \
		h[0] == 'P' and h[1] in '25' and h[2] in ' \t\n\r':
		return 'pgm'

tests.append(test_pgm)

def test_ppm(h, f):
	# PPM (portable pixmap)
	if len(h) >= 3 and \
		h[0] == 'P' and h[1] in '36' and h[2] in ' \t\n\r':
		return 'ppm'

tests.append(test_ppm)

def test_tiff(h, f):
	# TIFF (can be in Motorola or Intel byte order)
	if h[:2] in ('MM', 'II'):
		return 'tiff'

tests.append(test_tiff)

def test_rast(h, f):
	# Sun raster file
	if h[:4] == '\x59\xA6\x6A\x95':
		return 'rast'

tests.append(test_rast)

def test_xbm(h, f):
	# X bitmap (X10 or X11)
	s = '#define '
	if h[:len(s)] == s:
		return 'xbm'

tests.append(test_xbm)


#--------------------#
# Small test program #
#--------------------#

def test():
	import sys
	recursive = 0
	if sys.argv[1:] and sys.argv[1] == '-r':
		del sys.argv[1:2]
		recursive = 1
	try:
		if sys.argv[1:]:
			testall(sys.argv[1:], recursive, 1)
		else:
			testall(['.'], recursive, 1)
	except KeyboardInterrupt:
		sys.stderr.write('\n[Interrupted]\n')
		sys.exit(1)

def testall(list, recursive, toplevel):
	import sys
	import os
	for filename in list:
		if os.path.isdir(filename):
			print filename + '/:',
			if recursive or toplevel:
				print 'recursing down:'
				import glob
				names = glob.glob(os.path.join(filename, '*'))
				testall(names, recursive, 0)
			else:
				print '*** directory (use -r) ***'
		else:
			print filename + ':',
			sys.stdout.flush()
			try:
				print what(filename)
			except IOError:
				print '*** not found ***'
