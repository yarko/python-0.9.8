#! /ufs/guido/bin/sgi/python-405
#! /ufs/guido/bin/sgi/python

# Capture a continuous CMIF movie using the Indigo video library and board


# Usage:
#
# makemovie [-r rate] [-w width] [moviefile]


# Options:
#
# -r rate       : capture 1 out of every 'rate' frames (default 1)
# -w width      : initial window width (default interactive placement)
# -d		: drop fields if needed
# -g bits	: greyscale (2, 4 or 8 bits)
# -G            : 2-bit greyscale dithered
# -m		: monochrome dithered
# -M value	: monochrome tresholded with value
# -f		: Capture fields (in stead of frames)
# -n number     : Capture 'number' fields (default 60)
# 
# moviefile     : here goes the movie data (default film.video);
#                 the format is documented in cmif-film.ms


# User interface:
#
# Start the application.  Resize the window to the desired movie size.
# Press the left mouse button to start recording, release it to end
# recording.  You can record as many times as you wish, but each time
# you overwrite the output file(s), so only the last recording is
# kept.
#
# Press ESC or select the window manager Quit or Close window option
# to quit.  If you quit before recording anything, the output file(s)
# are not touched.


import sys
sys.path.append('/ufs/guido/src/video')
import sv, SV
import VFile
import gl, GL, DEVICE
import al, AL
import time
import posix
import getopt
import string
import imageop
import sgi

# Main program

def main():
	format = SV.RGB8_FRAMES
	rate = 1
	width = 0
	drop = 0
	mono = 0
	grey = 0
	greybits = 0
	monotreshold = -1
	fields = 0
	number = 60

	opts, args = getopt.getopt(sys.argv[1:], 'r:w:dg:mM:Gfn:')
	for opt, arg in opts:
		if opt == '-r':
			rate = string.atoi(arg)
			if rate < 2:
				sys.stderr.write('-r rate must be >= 2\n')
				sys.exit(2)
		elif opt == '-w':
			width = string.atoi(arg)
		elif opt == '-d':
			drop = 1
		elif opt == '-g':
			grey = 1
			greybits = string.atoi(arg)
			if not greybits in (2,4,8):
				print 'Only 2, 4 or 8 bit greyscale supported'
		elif opt == '-G':
			grey = 1
			greybits = -2
		elif opt == '-m':
			mono = 1
		elif opt == '-M':
			mono = 1
			monotreshold = string.atoi(arg)
		elif opt == '-f':
			fields = 1
		elif opt == '-n':
			number = string.atoi(arg)

	if args[2:]:
		sys.stderr.write('usage: Vrec [options] [file]\n')
		sys.exit(2)

	if args:
		filename = args[0]
	else:
		filename = 'film.video'

	v = sv.OpenVideo()
	# Determine maximum window size based on signal standard
	param = [SV.BROADCAST, 0]
	v.GetParam(param)
	if param[1] == SV.PAL:
		x = SV.PAL_XMAX
		y = SV.PAL_YMAX
	elif param[1] == SV.NTSC:
		x = SV.NTSC_XMAX
		y = SV.NTSC_YMAX
	else:
		print 'Unknown video standard', param[1]
		sys.exit(1)

	gl.foreground()
	gl.maxsize(x, y)
	gl.keepaspect(x, y)
	gl.stepunit(8, 6)
	if width:
		gl.prefsize(width, width*3/4)
	win = gl.winopen(filename)
	if width:
		gl.maxsize(x, y)
		gl.keepaspect(x, y)
		gl.stepunit(8, 6)
		gl.winconstraints()
	x, y = gl.getsize()
	print x, 'x', y

	v.SetSize(x, y)

	if drop:
		param = [SV.FIELDDROP, 1, SV.GENLOCK, SV.GENLOCK_OFF]
	else:
		param = [SV.FIELDDROP, 0, SV.GENLOCK, SV.GENLOCK_ON]
	if mono or grey:
		param = param+[SV.COLOR, SV.MONO, SV.INPUT_BYPASS, 1]
	else:
		param = param+[SV.COLOR, SV.DEFAULT_COLOR, SV.INPUT_BYPASS, 0]
	v.SetParam(param)

	v.BindGLWindow(win, SV.IN_REPLACE)

	gl.qdevice(DEVICE.LEFTMOUSE)
	gl.qdevice(DEVICE.WINQUIT)
	gl.qdevice(DEVICE.WINSHUT)
	gl.qdevice(DEVICE.ESCKEY)

	print 'Press left mouse to start recording'

	while 1:
		dev, val = gl.qread()
		if dev == DEVICE.LEFTMOUSE:
			if val == 1:
				info = format, x, y, number, rate
				record(v, info, filename, mono, grey, \
					  greybits, monotreshold, fields)
		elif dev == DEVICE.REDRAW:
			# Window resize (or move)
			x, y = gl.getsize()
			print x, 'x', y
			v.SetSize(x, y)
			v.BindGLWindow(win, SV.IN_REPLACE)
		elif dev in (DEVICE.ESCKEY, DEVICE.WINQUIT, DEVICE.WINSHUT):
			# Quit
			v.CloseVideo()
			gl.winclose(win)
			break


# Record until the mouse is released (or any other GL event)
# XXX audio not yet supported

def record(v, info, filename, mono, grey, greybits, monotreshold, fields):
	import thread
	format, x, y, number, rate = info
	fps = 59.64 # Fields per second
	# XXX (Strange: need fps of Indigo monitor, not of PAL or NTSC!)
	tpf = 1000.0 / fps # Time per field in msec
	#
	# Go grab
	#
	gl.wintitle('(rec) ' + filename)
	try:
		ninfo, data, bitvec = v.CaptureBurst(info)
	except sv.error, arg:
		print 'CaptureBurst failed:', arg
		print 'info:', info
		gl.wintitle(filename)
		return
	gl.wintitle('(save) '+ filename)
	#
	# Check results
	#
	if info <> ninfo:
		print 'Sorry, format changed.'
		print 'Wanted:',info
		print 'Got   :',ninfo
		gl.wintitle(filename)
		return
	# print bitvec
	if x*y*number <> len(data):
		print 'Funny data length: wanted',x,'*',y,'*', number,'=',\
			  x*y*number,'got',len(data)
		gl.wintitle(filename)
		return
	#
	# Save
	#
	if filename:
		#
		# Construct header and write it
		#
		vout = VFile.VoutFile().init(filename)
		if mono:
			vout.format = 'mono'
		elif grey and greybits == 8:
			vout.format = 'grey'
		elif grey:
			vout.format = 'grey'+`abs(greybits)`
		else:
			vout.format = 'rgb8'
		vout.width = x
		vout.height = y
		if fields:
			vout.packfactor = (1,-2)
		else:
			print 'Sorry, can only save fields at the moment'
			gl.wintitle(filename)
			return
		vout.writeheader()
		#
		# Compute convertor, if needed
		#
		convertor = None
		if grey:
			if greybits == 2:
				convertor = imageop.grey2grey2
			elif greybits == 4:
				convertor = imageop.grey2grey4
			elif greybits == -2:
				convertor = imageop.dither2grey2
		fieldsize = x*y/2
		nskipped = 0
		realframeno = 0
		tpf = 1000 / 50.0     #XXXX
		for frameno in range(0, number*2):
			if frameno <> 0 and \
				  bitvec[frameno] == bitvec[frameno-1]:
				nskipped = nskipped + 1
				continue
			#
			# Save field.
			# XXXX Works only for fields and top-to-bottom
			#
			start = frameno*fieldsize
			field = data[start:start+fieldsize]
			if convertor:
				field = convertor(field, x, y)
			elif mono and monotreshold >= 0:
				field = imageop.grey2mono(field, x, y, \
					  1, monotreshold)
			elif mono:
				field = imageop.dither2mono(field, x, y)
			vout.writeframe(int(realframeno*tpf), field, None)
		print 'Skipped',nskipped,'duplicate frames'
		vout.close()
			
	gl.wintitle('(done) ' + filename)

# Don't forget to call the main program

try:
	main()
except KeyboardInterrupt:
	print '[Interrupt]'
