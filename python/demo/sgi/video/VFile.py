# Classes to read and write CMIF video files.
# (For a description of the CMIF video format, see cmif-file.ms.)


# Layers of functionality:
#
# VideoParams: maintain essential parameters of a video file
# Displayer: display a frame in a window (with some extra parameters)
# Grabber: grab a frame from a window
# BasicVinFile: read a CMIF video file
# BasicVoutFile: write a CMIF video file
# VinFile: BasicVinFile + Displayer
# VoutFile: BasicVoutFile + Displayer + Grabber
#
# XXX Future extension:
# BasicVinoutFile: supports overwriting of individual frames


# Imported modules

import sys
import gl
import GL
import colorsys
import imageop


# Exception raised for various occasions

Error = 'VFile.Error'			# file format errors
CallError = 'VFile.CallError'		# bad call
AssertError = 'VFile.AssertError'	# internal malfunction


# Constants returned by gl.getdisplaymode(), from <gl/get.h>

DMRGB = 0
DMSINGLE = 1
DMDOUBLE = 2
DMRGBDOUBLE = 5


# Max nr. of colormap entries to use

MAXMAP = 4096 - 256


# Parametrizations of colormap handling based on color system.
# (These functions are used via eval with a constructed argument!)

def conv_grey(l, x, y):
	return colorsys.yiq_to_rgb(l, 0, 0)

def conv_grey4(l, x, y):
	return colorsys.yiq_to_rgb(l*17, 0, 0)

def conv_mono(l, x, y):
	return colorsys.yiq_to_rgb(l*255, 0, 0)

def conv_yiq(y, i, q):
	return colorsys.yiq_to_rgb(y, (i-0.5)*1.2, q-0.5)

def conv_hls(l, h, s):
	return colorsys.hls_to_rgb(h, l, s)

def conv_hsv(v, h, s):
	return colorsys.hsv_to_rgb(h, s, v)

def conv_rgb(r, g, b):
	raise Error, 'Attempt to make RGB colormap'

def conv_rgb8(rgb, d1, d2):
	rgb = int(rgb*255.0)
	r = (rgb >> 5) & 0x07
	g = (rgb     ) & 0x07
	b = (rgb >> 3) & 0x03
	return (r/7.0, g/7.0, b/3.0)

def conv_jpeg(r, g, b):
	raise Error, 'Attempt to make RGB colormap (jpeg)'

conv_jpeggrey = conv_grey
conv_grey2 = conv_grey


# Choose one of the above based upon a color system name

def choose_conversion(format):
	try:
		return eval('conv_' + format)
	except:
		raise Error, 'Unknown color system: ' + `format`


# Inverses of the above

def inv_grey(r, g, b):
	y, i, q = colorsys.rgb_to_yiq(r, g, b)
	return y, 0, 0

def inv_yiq(r, g, b):
	y, i, q = colorsys.rgb_to_yiq(r, g, b)
	return y, i/1.2 + 0.5, q + 0.5

def inv_hls(r, g, b):
	h, l, s = colorsys.rgb_to_hls(r, g, b)
	return l, h, s

def inv_hsv(r, g, b):
	h, s, v = colorsys.rgb_to_hsv(r, g, b)
	return v, h, s

def inv_rgb(r, g, b):
	raise Error, 'Attempt to invert RGB colormap'

def inv_rgb8(r, g, b):
	r = int(r*7.0)
	g = int(g*7.0)
	b = int(b*7.0)
	rgb = ((r&7) << 5) | ((b&3) << 3) | (g&7)
	return rgb / 255.0, 0, 0

def inv_jpeg(r, g, b):
	raise Error, 'Attempt to invert RGB colormap (jpeg)'

inv_jpeggrey = inv_grey


# Choose one of the above based upon a color system name

def choose_inverse(format):
	try:
		return eval('inv_' + format)
	except:
		raise Error, 'Unknown color system: ' + `format`


# Predicate to see whether this is an entry level (non-XS) Indigo.
# If so we can lrectwrite 8-bit wide pixels into a window in RGB mode

def is_entry_indigo():
	# XXX hack, hack.  We should call gl.gversion() but that doesn't
	# exist in earlier Python versions.  Therefore we check the number
	# of bitplanes *and* the size of the monitor.
	xmax = gl.getgdesc(GL.GD_XPMAX)
	if xmax <> 1024: return 0
	ymax = gl.getgdesc(GL.GD_YPMAX)
	if ymax != 768: return 0
	r = gl.getgdesc(GL.GD_BITS_NORM_SNG_RED)
	g = gl.getgdesc(GL.GD_BITS_NORM_SNG_GREEN)
	b = gl.getgdesc(GL.GD_BITS_NORM_SNG_BLUE)
	return (r, g, b) == (3, 3, 2)

#
# Predicate function to see whether this machine supports pixmode(PM_SIZE)
# with values 1 or 4.
#
# XXX Temporarily disabled, since it is unclear which machines support
# XXX which pixelsizes.
#
def support_packed_pixels():
	return 0   # To be architecture-dependent

# Routines to grab data, per color system (only a few really supported).
# (These functions are used via eval with a constructed argument!)

def grab_rgb(w, h, pf):
	if gl.getdisplaymode() <> DMRGB:
		raise Error, 'Sorry, can only grab rgb in single-buf rgbmode'
	if pf <> 1 and pf <> 0:
		raise Error, 'Sorry, only grab rgb with packfactor 1'
	return gl.lrectread(0, 0, w-1, h-1), None

def grab_rgb8(w, h, pf):
	if gl.getdisplaymode() <> DMRGB:
		raise Error, 'Sorry, can only grab rgb8 in single-buf rgbmode'
	if pf <> 1 and pf <> 0:
		raise Error, 'Sorry, can only grab rgb8 with packfactor 1'
	if not is_entry_indigo():
		raise Error, 'Sorry, can only grab rgb8 on entry level Indigo'
	# XXX Dirty Dirty here.
	# XXX Set buffer to cmap mode, grab image and set it back.
	gl.cmode()
	gl.gconfig()
	gl.pixmode(GL.PM_SIZE, 8)
	data = gl.lrectread(0, 0, w-1, h-1)
	data = data[:w*h]	# BUG FIX for python lrectread
	gl.RGBmode()
	gl.gconfig()
	gl.pixmode(GL.PM_SIZE, 32)
	return data, None

def grab_grey(w, h, pf):
	raise Error, 'Sorry, grabbing grey not implemented'

def grab_yiq(w, h, pf):
	raise Error, 'Sorry, grabbing yiq not implemented'

def grab_hls(w, h, pf):
	raise Error, 'Sorry, grabbing hls not implemented'

def grab_hsv(w, h, pf):
	raise Error, 'Sorry, grabbing hsv not implemented'

def grab_jpeg(w, h, pf):
	# XXX Ought to grab rgb and compress it
	raise Error, 'sorry, grabbing jpeg not implemented'

def grab_jpeggrey(w, h, pf):
	raise Error, 'sorry, grabbing jpeggrey not implemented'


# Choose one of the above based upon a color system name

def choose_grabber(format):
	try:
		return eval('grab_' + format)
	except:
		raise Error, 'Unknown color system: ' + `format`


# Base class to manage video format parameters

class VideoParams:

	# Initialize an instance.
	# Set all parameters to something decent
	# (except width and height are set to zero)

	def init(self):
		# Essential parameters
		self.format = 'grey'	# color system used
		# Choose from: grey, rgb, rgb8, hsv, yiq, hls, jpeg, jpeggrey,
		#              mono, grey2, grey4
		self.width = 0		# width of frame
		self.height = 0		# height of frame
		self.packfactor = 1	# expansion using rectzoom
		# if packfactor == 0, data is one 32-bit word/pixel;
		# otherwise, data is one byte/pixel
		self.c0bits = 8		# bits in first color dimension
		self.c1bits = 0		# bits in second color dimension
		self.c2bits = 0		# bits in third color dimension
		self.offset = 0		# colormap index offset (XXX ???)
		self.chrompack = 0	# set if separate chrominance data
		return self

	# Set the frame width and height (e.g. from gl.getsize())

	def setsize(self, width, height):
		self.width, self.height = width, height

	# Retrieve the frame width and height (e.g. for gl.prefsize())

	def getsize(self):
		return (self.width, self.height)

	# Set all parameters.
	# This does limited validity checking;
	# if the check fails no parameters are changed

	def setinfo(self, values):
		(self.format, self.width, self.height, self.packfactor,\
			self.c0bits, self.c1bits, self.c2bits, self.offset, \
			self.chrompack) = values

	# Retrieve all parameters in a format suitable for a subsequent
	# call to setinfo()

	def getinfo(self):
		return (self.format, self.width, self.height, self.packfactor,\
			self.c0bits, self.c1bits, self.c2bits, self.offset, \
			self.chrompack)

	# Write the relevant bits to stdout

	def printinfo(self):
		print 'Format:  ', self.format
		print 'Size:    ', self.width, 'x', self.height
		print 'Pack:    ', self.packfactor, '; chrom:', self.chrompack
		print 'Bits:    ', self.c0bits, self.c1bits, self.c2bits
		print 'Offset:  ', self.offset

	# Calculate data size, if possible
	def calcframesize(self):
		if self.format == 'rgb':
			return self.width*self.height*4
		if self.format in ('jpeg', 'jpeggrey'):
			raise CallError
		if type(self.packfactor) == type(()):
			xpf, ypf = self.packfactor
		else:
			xpf = ypf = self.packfactor
		if ypf < 0: ypf = -ypf
		size = (self.width/xpf)*(self.height/ypf)
		if self.format == 'grey4':
			size = (size+1)/2
		elif self.format == 'grey2':
			size = (size+3)/4
		elif self.format == 'mono':
			size = (size+7)/8
		return size


# Class to display video frames in a window.
# It is the caller's responsibility to ensure that the correct window
# is current when using showframe(), initcolormap(), clear() and clearto()

class Displayer(VideoParams):

	# Initialize an instance.
	# This does not need a current window

	def init(self):
		self = VideoParams.init(self)
		# User-settable parameters
		self.magnify = 1.0	# frame magnification factor
		self.xorigin = 0	# x frame offset
		self.yorigin = 0	# y frame offset (from bottom)
		self.quiet = 0		# if set, don't print messages
		self.fallback = 1	# allow fallback to grey
		# Internal flags
		self.colormapinited = 0	# must initialize window
		self.skipchrom = 0	# don't skip chrominance data
		self.color0 = None	# magic, used by clearto()
		self.fixcolor0 = 0	# don't need to fix color0
		self.mustunpack = (not support_packed_pixels())
		return self

	# setinfo() must reset some internal flags

	def setinfo(self, values):
		VideoParams.setinfo(self, values)
		self.colormapinited = 0
		self.skipchrom = 0
		self.color0 = None
		self.fixcolor0 = 0

	# Show one frame, initializing the window if necessary

	def showframe(self, data, chromdata):
		self.showpartframe(data, chromdata, \
			  (0,0,self.width,self.height))

	def showpartframe(self, data, chromdata, (x,y,w,h)):
		pf = self.packfactor
		pmsize = 8
		if pf:
			if type(pf) == type(()):
				xpf, ypf = pf
			else:
				xpf = ypf = pf
			if ypf < 0:
				gl.pixmode(GL.PM_TTOB, 1)
				ypf = -ypf
			if xpf < 0:
				gl.pixmode(GL.PM_RTOL, 1)
				xpf = -xpf
		else:
			xpf = ypf = 1
		if self.format in ('jpeg', 'jpeggrey'):
			import jpeg
			data, width, height, bytes = jpeg.decompress(data)
			if self.format == 'jpeg':
				b = 4
				xp = yp = 1
			else:
				b = 1
				xp = xpf
				yp = ypf
			if (width, height, bytes) <> (w/xp, h/yp, b):
				raise Error, 'jpeg data has wrong size'
		elif self.format in ('mono', 'grey4'):
			if self.mustunpack:
				if self.format == 'mono':
					data = imageop.mono2grey(data, \
						  w/xpf, h/ypf, 0x20, 0xdf)
				elif self.format == 'grey4':
					data = imageop.grey42grey(data, \
						  w/xpf, h/ypf)
			else:
				# We don't need to unpack, the hardware
				# can do it.
				if self.format == 'mono':
					pmsize = 1
				else:
					pmsize = 4
		elif self.format == 'grey2':
			data = imageop.grey22grey(data, w/xpf, h/ypf)
		if not self.colormapinited:
			self.initcolormap()
		if self.fixcolor0:
			gl.mapcolor(self.color0)
			self.fixcolor0 = 0
		xfactor = yfactor = self.magnify
		if pf:
			xfactor = xfactor * xpf
			yfactor = yfactor * ypf
		if chromdata and not self.skipchrom:
			cp = self.chrompack
			cx = int(x*xfactor*cp) + self.xorigin
			cy = int(y*yfactor*cp) + self.yorigin
			cw = (w+cp-1)/cp
			ch = (h+cp-1)/cp
			gl.rectzoom(xfactor*cp, yfactor*cp)
			gl.pixmode(GL.PM_SIZE, 16)
			gl.writemask(self.mask - ((1 << self.c0bits) - 1))
			gl.lrectwrite(cx, cy, cx + cw - 1, cy + ch - 1, \
				  chromdata)
		#
		if pf:
			gl.writemask((1 << self.c0bits) - 1)
			gl.pixmode(GL.PM_SIZE, pmsize)
			w = w/xpf
			h = h/ypf
			x = x/xpf
			y = y/ypf
		gl.rectzoom(xfactor, yfactor)
		x = int(x*xfactor)+self.xorigin
		y = int(y*yfactor)+self.yorigin
		gl.lrectwrite(x, y, x + w - 1, y + h - 1, data)
		gl.gflush()

	# Initialize the window: set RGB or colormap mode as required,
	# fill in the colormap, and clear the window

	def initcolormap(self):
		self.colormapinited = 1
		self.color0 = None
		self.fixcolor0 = 0
		if self.format in ('rgb', 'jpeg'):
			gl.RGBmode()
			gl.gconfig()
			gl.RGBcolor(200, 200, 200) # XXX rather light grey
			gl.clear()
			return
		# This only works on an Entry-level Indigo from IRIX 4.0.5
		if self.format == 'rgb8' and is_entry_indigo() and \
			  gl.gversion() == 'GL4DLG-4.0.': # Note trailing '.'!
			gl.RGBmode()
			gl.gconfig()
			gl.RGBcolor(200, 200, 200) # XXX rather light grey
			gl.clear()
			gl.pixmode(GL.PM_SIZE, 8)
			return
		gl.cmode()
		gl.gconfig()
		self.skipchrom = 0
		if self.offset == 0:
			self.mask = 0x7ff
		else:
			self.mask = 0xfff
		if not self.quiet:
			sys.stderr.write('Initializing color map...')
		self._initcmap()
		gl.clear()
		if not self.quiet:
			sys.stderr.write(' Done.\n')

	# Clear the window to a default color

	def clear(self):
		if not self.colormapinited: raise CallError
		if gl.getdisplaymode() in (DMRGB, DMRGBDOUBLE):
			gl.RGBcolor(200, 200, 200) # XXX rather light grey
			gl.clear()
			return
		gl.writemask(0xffffffff)
		gl.clear()

	# Clear the window to a given RGB color.
	# This may steal the first color index used; the next call to
	# showframe() will restore the intended mapping for that index

	def clearto(self, r, g, b):
		if not self.colormapinited: raise CallError
		if gl.getdisplaymode() in (DMRGB, DMRGBDOUBLE):
			gl.RGBcolor(r, g, b)
			gl.clear()
			return
		index = self.color0[0]
		self.fixcolor0 = 1
		gl.mapcolor(index, r, g, b)
		gl.writemask(0xffffffff)
		gl.clear()
		gl.gflush()

	# Do the hard work for initializing the colormap (internal).
	# This also sets the current color to the first color index
	# used -- the caller should never change this since it is used
	# by clear() and clearto()

	def _initcmap(self):
		if self.format in ('mono', 'grey4') and self.mustunpack:
			convcolor = conv_grey
		else:
			convcolor = choose_conversion(self.format)
		maxbits = gl.getgdesc(GL.GD_BITS_NORM_SNG_CMODE)
		if maxbits > 11:
			maxbits = 11
		c0bits = self.c0bits
		c1bits = self.c1bits
		c2bits = self.c2bits
		if c0bits+c1bits+c2bits > maxbits:
			if self.fallback and c0bits < maxbits:
				# Cannot display frames in this mode, use grey
				self.skipchrom = 1
				c1bits = c2bits = 0
				convcolor = choose_conversion('grey')
			else:
				raise Error, 'Sorry, '+`maxbits`+ \
				  ' bits max on this machine'
		maxc0 = 1 << c0bits
		maxc1 = 1 << c1bits
		maxc2 = 1 << c2bits
		if self.offset == 0 and maxbits == 11:
			offset = 2048
		else:
			offset = self.offset
		if maxbits <> 11:
			offset = offset & ((1<<maxbits)-1)
		self.color0 = None
		self.fixcolor0 = 0
		for c0 in range(maxc0):
			c0v = c0/float(maxc0-1)
			for c1 in range(maxc1):
				if maxc1 == 1:
					c1v = 0
				else:
					c1v = c1/float(maxc1-1)
				for c2 in range(maxc2):
					if maxc2 == 1:
						c2v = 0
					else:
						c2v = c2/float(maxc2-1)
					index = offset + c0 + (c1<<c0bits) + \
						(c2 << (c0bits+c1bits))
					if index < MAXMAP:
						rv, gv, bv = \
						  convcolor(c0v, c1v, c2v)
						r, g, b = int(rv*255.0), \
							  int(gv*255.0), \
							  int(bv*255.0)
						gl.mapcolor(index, r, g, b)
						if self.color0 == None:
							self.color0 = \
								index, r, g, b
		# Permanently make the first color index current
		gl.color(self.color0[0])
		gl.gflush() # send the colormap changes to the X server


# Class to grab frames from a window.
# (This has fewer user-settable parameters than Displayer.)
# It is the caller's responsibility to initialize the window and to
# ensure that it is current when using grabframe()

class Grabber(VideoParams):

	# XXX The init() method of VideoParams is just fine, for now

	# Grab a frame.
	# Return (data, chromdata) just like getnextframe().

	def grabframe(self):
		grabber = choose_grabber(self.format)
		return grabber(self.width, self.height, self.packfactor)


# Read a CMIF video file header.
# Return (version, values) where version is 0.0, 1.0, 2.0 or 3.[01],
# and values is ready for setinfo().
# Raise Error if there is an error in the info

def readfileheader(fp, filename):
	#
	# Get identifying header
	#
	line = fp.readline(20)
	if   line == 'CMIF video 0.0\n':
		version = 0.0
	elif line == 'CMIF video 1.0\n':
		version = 1.0
	elif line == 'CMIF video 2.0\n':
		version = 2.0
	elif line == 'CMIF video 3.0\n':
		version = 3.0
	elif line == 'CMIF video 3.1\n':
		version = 3.1
	else:
		# XXX Could be version 0.0 without identifying header
		raise Error, \
			filename + ': Unrecognized file header: ' + `line`[:20]
	#
	# Get color encoding info
	# (The format may change to 'rgb' later when packfactor == 0)
	#
	if version <= 1.0:
		format = 'grey'
		c0bits, c1bits, c2bits = 8, 0, 0
		chrompack = 0
		offset = 0
	elif version == 2.0:
		line = fp.readline()
		try:
			c0bits, c1bits, c2bits, chrompack = eval(line[:-1])
		except:
			raise Error, filename + ': Bad 2.0 color info'
		if c1bits or c2bits:
			format = 'yiq'
		else:
			format = 'grey'
		offset = 0
	elif version in (3.0, 3.1):
		line = fp.readline()
		try:
			format, rest = eval(line[:-1])
		except:
			raise Error, filename + ': Bad 3.[01] color info'
		if format == 'xrgb8':
			format = 'rgb8' # rgb8 upside-down, for X
		if format in ('rgb', 'jpeg'):
			c0bits = c1bits = c2bits = 0
			chrompack = 0
			offset = 0
		elif format in ('grey', 'jpeggrey', 'mono', 'grey2', 'grey4'):
			c0bits = rest
			c1bits = c2bits = 0
			chrompack = 0
			offset = 0
		else:
			# XXX ought to check that the format is valid
			try:
			    c0bits, c1bits, c2bits, chrompack, offset = rest
			except:
			    raise Error, filename + ': Bad 3.[01] color info'
	#
	# Get frame geometry info
	#
	line = fp.readline()
	try:
		x = eval(line[:-1])
	except:
		raise Error, filename + ': Bad (w,h,pf) info'
	if type(x) <> type(()):
		raise Error, filename + ': Bad (w,h,pf) info'
	if len(x) == 3:
		width, height, packfactor = x
		if packfactor == 0 and version < 3.0:
			format = 'rgb'
			c0bits = 0
	elif len(x) == 2 and version <= 1.0:
		width, height = x
		packfactor = 2
	else:
		raise Error, filename + ': Bad (w,h,pf) info'
	if type(packfactor) == type(()):
		xpf, ypf = packfactor
		xpf = abs(xpf)
		ypf = abs(ypf)
		width = (width/xpf) * xpf
		height = (height/ypf) * ypf
	elif packfactor > 1:
		width = (width / packfactor) * packfactor
		height = (height / packfactor) * packfactor
	#
	# Return (version, values)
	#
	values = (format, width, height, packfactor, \
		  c0bits, c1bits, c2bits, offset, chrompack)
	return (version, values)


# Read a *frame* header -- separate functions per version.
# Return (timecode, datasize, chromdatasize).
# Raise EOFError if end of data is reached.
# Raise Error if data is bad.

def readv0frameheader(fp):
	line = fp.readline()
	if not line or line == '\n': raise EOFError
	try:
		t = eval(line[:-1])
	except:
		raise Error, 'Bad 0.0 frame header'
	return (t, 0, 0)

def readv1frameheader(fp):
	line = fp.readline()
	if not line or line == '\n': raise EOFError
	try:
		t, datasize = eval(line[:-1])
	except:
		raise Error, 'Bad 1.0 frame header'
	return (t, datasize, 0)

def readv2frameheader(fp):
	line = fp.readline()
	if not line or line == '\n': raise EOFError
	try:
		t, datasize = eval(line[:-1])
	except:
		raise Error, 'Bad 2.0 frame header'
	return (t, datasize, 0)

def readv3frameheader(fp):
	line = fp.readline()
	if not line or line == '\n': raise EOFError
	try:
		t, datasize, chromdatasize = x = eval(line[:-1])
	except:
		raise Error, 'Bad 3.[01] frame header'
	return x


# Write a CMIF video file header (always version 3.1)

def writefileheader(fp, values):
	(format, width, height, packfactor, \
		c0bits, c1bits, c2bits, offset, chrompack) = values
	#
	# Write identifying header
	#
	fp.write('CMIF video 3.1\n')
	#
	# Write color encoding info
	#
	if format in ('rgb', 'jpeg'):
		data = (format, 0)
	elif format in ('grey', 'jpeggrey', 'mono', 'grey2', 'grey4'):
		data = (format, c0bits)
	else:
		data = (format, (c0bits, c1bits, c2bits, chrompack, offset))
	fp.write(`data`+'\n')
	#
	# Write frame geometry info
	#
	if format in ('rgb', 'jpeg'):
		packfactor = 0
	elif packfactor == 0:
		packfactor = 1
	data = (width, height, packfactor)
	fp.write(`data`+'\n')


# Basic class for reading CMIF video files

class BasicVinFile(VideoParams):

	def init(self, filename):
		if filename == '-':
			fp = sys.stdin
		else:
			fp = open(filename, 'r')
		return self.initfp(fp, filename)

	def initfp(self, fp, filename):
		self = VideoParams.init(self)
		self.fp = fp
		self.filename = filename
		self.version, values = readfileheader(fp, filename)
		VideoParams.setinfo(self, values)
		if self.version == 0.0:
			w, h, pf = self.width, self.height, self.packfactor
			if pf == 0:
				self._datasize = w*h*4
			else:
				self._datasize = (w/pf) * (h/pf)
			self._readframeheader = self._readv0frameheader
		elif self.version == 1.0:
			self._readframeheader = readv1frameheader
		elif self.version == 2.0:
			self._readframeheader = readv2frameheader
		elif self.version in (3.0, 3.1):
			self._readframeheader = readv3frameheader
		else:
			raise Error, \
				filename + ': Bad version: ' + `self.version`
		self.framecount = 0
		self.atframeheader = 1
		self.eofseen = 0
		self.errorseen = 0
		try:
			self.startpos = self.fp.tell()
			self.canseek = 1
		except IOError:
			self.startpos = -1
			self.canseek = 0
		return self

	def _readv0frameheader(self, fp):
		t, ds, cs = readv0frameheader(fp)
		ds = self._datasize
		return (t, ds, cs)

	def close(self):
		self.fp.close()
		del self.fp
		del self._readframeheader

	def setinfo(self, values):
		raise CallError # Can't change info of input file!

	def setsize(self, width, height):
		raise CallError # Can't change info of input file!

	def rewind(self):
		if not self.canseek:
			raise Error, self.filename + ': can\'t seek'
		self.fp.seek(self.startpos)
		self.framecount = 0
		self.atframeheader = 1
		self.eofseen = 0
		self.errorseen = 0

	def warmcache(self):
		print '[BasicVinFile.warmcache() not implemented]'

	def printinfo(self):
		print 'File:    ', self.filename
		print 'Size:    ', getfilesize(self.filename)
		print 'Version: ', self.version
		VideoParams.printinfo(self)

	def getnextframe(self):
		t, ds, cs = self.getnextframeheader()
		data, cdata = self.getnextframedata(ds, cs)
		return (t, data, cdata)

	def skipnextframe(self):
		t, ds, cs = self.getnextframeheader()
		self.skipnextframedata(ds, cs)
		return t

	def getnextframeheader(self):
		if self.eofseen: raise EOFError
		if self.errorseen: raise CallError
		if not self.atframeheader: raise CallError
		self.atframeheader = 0
		try:
			return self._readframeheader(self.fp)
		except Error, msg:
			self.errorseen = 1
			# Patch up the error message
			raise Error, self.filename + ': ' + msg
		except EOFError:
			self.eofseen = 1
			raise EOFError

	def getnextframedata(self, ds, cs):
		if self.eofseen: raise EOFError
		if self.errorseen: raise CallError
		if self.atframeheader: raise CallError
		if ds:
			data = self.fp.read(ds)
			if len(data) < ds:
				self.eofseen = 1
				raise EOFError
		else:
			data = ''
		if cs:
			cdata = self.fp.read(cs)
			if len(cdata) < cs:
				self.eofseen = 1
				raise EOFError
		else:
			cdata = ''
		self.atframeheader = 1
		self.framecount = self.framecount + 1
		return (data, cdata)

	def skipnextframedata(self, ds, cs):
		if self.eofseen: raise EOFError
		if self.errorseen: raise CallError
		if self.atframeheader: raise CallError
		# Note that this won't raise EOFError for a partial frame
		# since there is no easy way to tell whether a seek
		# ended up beyond the end of the file
		if self.canseek:
			self.fp.seek(ds + cs, 1) # Relative seek
		else:
			dummy = self.fp.read(ds + cs)
			del dummy
		self.atframeheader = 1
		self.framecount = self.framecount + 1


# Subroutine to return a file's size in bytes

def getfilesize(filename):
	import os, stat
	try:
		st = os.stat(filename)
		return st[stat.ST_SIZE]
	except os.error:
		return 0


# Derived class implementing random access and index cached in the file

class RandomVinFile(BasicVinFile):

	def initfp(self, fp, filename):
		self = BasicVinFile.initfp(self, fp, filename)
		self.index = []
		return self

	def warmcache(self):
		if len(self.index) == 0:
			try:
				self.readcache()
			except Error:
				self.buildcache()
		else:
			print '[RandomVinFile.warmcache(): too late]'
			self.rewind()

	def buildcache(self):
		self.index = []
		self.rewind()
		while 1:
			try: dummy = self.skipnextframe()
			except EOFError: break
		self.rewind()

	def writecache(self):
		# Raises IOerror if the file is not seekable & writable!
		import marshal
		if len(self.index) == 0:
			self.buildcache()
			if len(self.index) == 0:
				raise Error, self.filename + ': No frames'
		self.fp.seek(0, 2)
		self.fp.write('\n/////CMIF/////\n')
		pos = self.fp.tell()
		data = `pos`
		data = '\n-*-*-CMIF-*-*-\n' + data + ' '*(15-len(data)) + '\n'
		try:
			marshal.dump(self.index, self.fp)
			self.fp.write(data)
			self.fp.flush()
		finally:
			self.rewind()

	def readcache(self):
		# Raises Error if there is no cache in the file
		import marshal
		if len(self.index) <> 0:
			raise CallError
		self.fp.seek(-32, 2)
		data = self.fp.read()
		if data[:16] <> '\n-*-*-CMIF-*-*-\n' or data[-1:] <> '\n':
			self.rewind()
			raise Error, self.filename + ': No cache'
		pos = eval(data[16:-1])
		self.fp.seek(pos)
		try:
			self.index = marshal.load(self.fp)
		except TypeError:
			self.rewind()
			raise Error, self.filename + ': Bad cache'
		self.rewind()

	def getnextframeheader(self):
		if self.framecount < len(self.index):
			return self._getindexframeheader(self.framecount)
		if self.framecount > len(self.index):
			raise AssertError, \
				'managed to bypass index?!?'
		rv = BasicVinFile.getnextframeheader(self)
		if self.canseek:
			pos = self.fp.tell()
			self.index.append(rv, pos)
		return rv

	def getrandomframe(self, i):
		t, ds, cs = self.getrandomframeheader(i)
		data, cdata = self.getnextframedata()
		return t, ds, cs

	def getrandomframeheader(self, i):
		if i < 0: raise ValueError, 'negative frame index'
		if not self.canseek:
			raise Error, self.filename + ': can\'t seek'
		if i < len(self.index):
			return self._getindexframeheader(i)
		if len(self.index) > 0:
			rv = self.getrandomframeheader(len(self.index)-1)
		else:
			self.rewind()
			rv = self.getnextframeheader()
		while i > self.framecount:
			self.skipnextframedata()
			rv = self.getnextframeheader()
		return rv

	def _getindexframeheader(self, i):
		(rv, pos) = self.index[i]
		self.fp.seek(pos)
		self.framecount = i
		self.atframeheader = 0
		self.eofseen = 0
		self.errorseen = 0
		return rv


# Basic class for writing CMIF video files

class BasicVoutFile(VideoParams):

	def init(self, filename):
		if filename == '-':
			fp = sys.stdout
		else:
			fp = open(filename, 'w')
		return self.initfp(fp, filename)

	def initfp(self, fp, filename):
		self = VideoParams.init(self)
		self.fp = fp
		self.filename = filename
		self.version = 3.0 # In case anyone inquries
		self.headerwritten = 0
		return self

	def flush(self):
		self.fp.flush()

	def close(self):
		self.fp.close()
		del self.fp

	def prealloc(self, nframes):
		if not self.headerwritten: raise CallError
		data = '\xff' * self.calcframesize()
		pos = self.fp.tell()
		for i in range(nframes):
			self.fp.write(data)
		self.fp.seek(pos)

	def setinfo(self, values):
		if self.headerwritten: raise CallError
		VideoParams.setinfo(self, values)

	def writeheader(self):
		if self.headerwritten: raise CallError
		writefileheader(self.fp, self.getinfo())
		self.headerwritten = 1
		self.atheader = 1
		self.framecount = 0

	def rewind(self):
		self.fp.seek(0)
		self.headerwritten = 0
		self.atheader = 1
		self.framecount = 0

	def printinfo(self):
		print 'File:    ', self.filename
		VideoParams.printinfo(self)

	def writeframe(self, t, data, cdata):
		if data: ds = len(data)
		else: ds = 0
		if cdata: cs = len(cdata)
		else: cs = 0
		self.writeframeheader(t, ds, cs)
		self.writeframedata(data, cdata)

	def writeframeheader(self, t, ds, cs):
		if not self.headerwritten: self.writeheader()
		if not self.atheader: raise CallError
		data = `(t, ds, cs)`
		n = len(data)
		if n < 63: data = data + ' '*(63-n)
		self.fp.write(data + '\n')
		self.atheader = 0

	def writeframedata(self, data, cdata):
		if not self.headerwritten or self.atheader: raise CallError
		if data: self.fp.write(data)
		if cdata: self.fp.write(cdata)
		self.atheader = 1
		self.framecount = self.framecount + 1


# Classes that combine files with displayers and/or grabbers:

class VinFile(RandomVinFile, Displayer):

	def initfp(self, fp, filename):
		self = Displayer.init(self)
		return RandomVinFile.initfp(self, fp, filename)

	def shownextframe(self):
		t, data, cdata = self.getnextframe()
		self.showframe(data, cdata)
		return t


class VoutFile(BasicVoutFile, Displayer, Grabber):

	def initfp(self, fp, filename):
		self = Displayer.init(self)
##		self = Grabber.init(self) # XXX not needed
		return BasicVoutFile.initfp(self, fp, filename)


# Simple test program (VinFile only)

def test():
	import time
	if sys.argv[1:]: filename = sys.argv[1]
	else: filename = 'film.video'
	vin = VinFile().init(filename)
	vin.printinfo()
	gl.foreground()
	gl.prefsize(vin.getsize())
	wid = gl.winopen(filename)
	vin.initcolormap()
	t0 = time.millitimer()
	while 1:
		try: t, data, cdata = vin.getnextframe()
		except EOFError: break
		dt = t0 + t - time.millitimer()
		if dt > 0: time.millisleep(dt)
		vin.showframe(data, cdata)
	time.sleep(2)
