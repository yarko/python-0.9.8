#!/ufs/guido/bin/sgi/python
# Stuff to parse files produced by recordaiff.
#
# An AIFF file has the following structure.
#
#	+-----------------+
#	| FORM            |
#	+-----------------+
#	| <size>          |
#	+----+------------+
#	|    | AIFF       |
#	|    +------------+
#	|    | <chunks>   |
#	|    |    .       |
#	|    |    .       |
#	|    |    .       |
#	+----+------------+
#
# A chunk consists of an identifier (4 bytes) followed by a size (4 bytes,
# big endian order), followed by the data.  The size field does not include
# the size of the 8 byte header.
#
# The following chunk types are recognized.
#
#	COMM
#		<# of channels> (2 bytes)
#		<# of sound frames> (4 bytes)
#		<size of the samples> (2 bytes)
#		<sampling frequency> (10 bytes, IEEE 80-bit extended
#			floating point)
#	SSND
#		<offset> (4 bytes, not used by this program)
#		<blocksize> (4 bytes, not used by this program)
#		<sound data>
#
# Usage.
#
# Reading AIFF files:
#	f = Aiff().init(file, 'r')
# You can then read the audio samples using f.readsamps(nframes).
# Audio parameters are available as f.sampwidth, f.samprate, f.nchannels.
# These parameters are in AL format (AL.STEREO, etc.)
#
# Writing AIFF files:
#	f = Aiff().init(file, 'w')
# You should then set the audio parameters f.sampwidth, f.samprate, and
# f.nchannels, using the AL names.  You can also use f.setnsamps(nframes)
# to set the number of frames to be written.  After this, you can write the
# samples using f.writesamps(data) or f.writesampsraw(data).  Finally, you
# should call f.destroy().  When the number of frames was set using
# f.setnsamps(nframes), the number of frames should match what is actually
# written.  If it does, no seeks are attempted.

import AL
import math

Error = 'aiff.Error'

# known sampling rates
samprates =	(48000, AL.RATE_48000), \
		(44100, AL.RATE_44100), \
		(32000, AL.RATE_32000), \
		(22050, AL.RATE_22050), \
		(16000, AL.RATE_16000), \
		(11025, AL.RATE_11025), \
		( 8000,  AL.RATE_8000)

def read_chunk_header(f): # 8 bytes
	type = f.read(4)
	if type == '':
		raise EOFError
	if len(type) < 4:
		raise Error, 'short type identifier: ' + type
	size = read_long(f)
	return type, size

def read_form_chunk(f): # 4 bytes
	if f.read(4) <> 'AIFF':
		raise Error, 'form chunk does not begin with AIFF id'

def read_comm_chunk(f): # 18 bytes
	nchannels = read_short(f)
	nsampframes = read_long(f)
	sampwidth = read_short(f)
	samprate = read_ieee_extended(f)
	return nchannels, nsampframes, sampwidth, samprate

def read_ssnd_chunk(f):
	offset = read_long(f)
	blocksize = read_long(f)
	return offset, blocksize
	# Now you need to read the data as well!

# unrecognized chunk types
skiplist = 'MARK', 'INST', 'APPL', 'MIDI', 'AESD', 'COMT', \
	   'NAME', 'AUTH', '(c) ', 'ANNO'

def skip_chunk(f, size):
	try:
		f.seek(size, 1)
	except RuntimeError:
		while size > 0:
			bufsize = min(size, 8192)
			dummy = f.read(bufsize)
			if not dummy: return
			size = size - len(dummy)

def read_short(f): # 2 byte
	x = 0
	for i in range(2):
		byte = f.read(1)
		if byte == '': raise EOFError
		x = x*256 + ord(byte)
	if x >= 0x8000:
		x = x - 0x10000
	return x

def read_long(f): # 4 bytes
	x = read_ulong(f)
	if x >= 0x80000000L:
		x = x - 0x100000000L
	x = int(x)
	return x

def read_ulong(f): # 4 bytes
	x = 0L
	for i in range(4):
		byte = f.read(1)
		if byte == '': raise EOFError
		x = x*256 + ord(byte)
	return x

def write_long(f, x):
	if x < 0:
		x = x + 0x100000000L
	data = []
	for i in range(4):
		d, m = divmod(x, 256)
		data.insert(0, m)
		x = d
	for i in range(4):
		f.write(chr(int(data[i])))

def write_short(f, x):
	d, m = divmod(x, 256)
	f.write(chr(d))
	f.write(chr(m))

HUGE_VAL = 1.79769313486231e+308 # See <limits.h>

def read_ieee_extended(f): # 10 bytes
	expon = read_short(f) # 2 bytes
	sign = 1
	if expon < 0:
		sign = -1
		expon = expon + 0x8000
	himant = read_ulong(f) # 4 bytes
	lomant = read_ulong(f) # 4 bytes
	if expon == himant == lomant == 0:
		f = 0.0
	elif expon == 0x7FFF:
		f = HUGE_VAL
	else:
		expon = expon - 16383
		f = (himant * 0x100000000L + lomant) * pow(2.0, expon - 63)
	return sign * f

def write_ieee_extended(f, x):
	if x < 0:
		sign = 0x8000
		x = x * -1
	else:
		sign = 0
	if x == 0:
		expon = 0
		himant = 0
		lomant = 0
	else:
		fmant, expon = math.frexp(x)
		if expon > 16384 or fmant >= 1:		# Infinity or NaN
			expon = sign|0x7FFF
			himant = 0
			lomant = 0
		else:					# Finite
			expon = expon + 16382
			if expon < 0:			# denormalized
				fmant = math.ldexp(fmant, expon)
				expon = 0
			expon = expon | sign
			fmant = math.ldexp(fmant, 32)
			fsmant = math.floor(fmant)
			himant = long(fsmant)
			fmant = math.ldexp(fmant - fsmant, 32)
			fsmant = math.floor(fmant)
			lomant = long(fsmant)
	write_short(f, expon)
	write_long(f, himant)
	write_long(f, lomant)

def comm2al(nchannels, nsampframes, sampwidth, samprate):
	if nchannels == 1:
		nchannels = AL.MONO
	elif nchannels == 2:
		nchannels = AL.STEREO
	else:
		raise Error, 'bad number of channels'
	for t in samprates:
		if samprate == t[0]:
			samprate = t[1]
			break
	else:
		raise Error, 'bad sample rate'
	if sampwidth == 8:
		sampwidth = AL.SAMPLE_8
	elif sampwidth == 16:
		sampwidth = AL.SAMPLE_16
	elif sampwidth == 24:
		sampwidth = AL.SAMPLE_24
	else:
		raise Error, 'bad sample width'
	return nchannels, nsampframes, sampwidth, samprate

def al2comm(nchannels, sampwidth, samprate):
	if nchannels == AL.MONO:
		nchannels = 1
	elif nchannels == AL.STEREO:
		nchannels = 2
	else:
		raise Error, 'bad number of channels'
	for t in samprates:
		if samprate == t[1]:
			samprate = t[0]
			break
	else:
		raise Error, 'bad sample rate'
	if sampwidth == AL.SAMPLE_8:
		sampwidth = 8
	elif sampwidth == AL.SAMPLE_16:
		sampwidth = 16
	elif sampwidth == AL.SAMPLE_24:
		sampwidth = 24
	else:
		raise Error, 'bad sample width'
	return nchannels, sampwidth, samprate

def write_form(f, datasize):
	f.write('FORM')
	write_long(f, datasize)
	f.write('AIFF')

def write_comm(f, nchannels, nsampframes, sampwidth, samprate):
	f.write('COMM')
	write_long(f, 18)
	write_short(f, nchannels)
	write_long(f, nsampframes)
	write_short(f, sampwidth)
	write_ieee_extended(f, samprate)

def write_ssnd(f, datasize):
	f.write('SSND')
	write_long(f, datasize)
	write_long(f, 0)
	write_long(f, 0)

def patchsize(f, nsampframes, datasize):
	curpos = f.tell()
	f.seek(4, 0)
	write_long(f, datasize + 46)
	f.seek(22, 0)
	write_long(f, nsampframes)
	f.seek(42, 0)
	write_long(f, datasize + 8)
	f.seek(curpos, 0)			# seek back

class Aiff():
	def init(self, filename, mode):
		if mode[1:] == 'f':
			self.file = filename
			self.filename = 'NoName'
		else:
			self.filename = filename
		self.mode = mode
		if mode == 'r' or mode == 'rf':
			return self.init_read()
		elif mode == 'w' or mode == 'wf':
			return self.init_write()
		else:
			raise Error, 'bad mode'
#
	def destroy(self):
		if self.mode[0] == 'w':
			if self._totnsampframesset and self.nsampframes != self._totnsampframes:
				raise Error, 'not enough data written'
			if (self.nsampframes * self.nchannels * self.sampwidth) % 2 == 1:
				# pad to even size
				self.file.write('\0')
			if not self._totnsampframesset:
				patchsize(self.file, self.nsampframes, self.nsampframes * self.nchannels * self.sampwidth)
			self.file.flush()
		self.file.close()
		self.file = None
#
	def init_read(self):
		if self.mode == 'r':
			self.file = open(self.filename, 'r')
		type, size = read_chunk_header(self.file)
		if type != 'FORM':
			raise Error, 'file does not begin with FORM id'
		if size <= 0:
			raise Error, 'invalid FORM chunk data size'
		read_form_chunk(self.file)
		while 1:
			type, size = read_chunk_header(self.file)
			if type == 'COMM':
				self.nchannels, self.nsampframes, \
					self.sampwidth, self.samprate = \
						comm2al(read_comm_chunk(self.file))
			elif type == 'SSND':
				self.offset, self.blocksize = \
					read_ssnd_chunk(self.file)
				break
			else:
				for i in skiplist:
					if type == i:
						skip_chunk(self.file, size)
						break
				else:
					raise Error, 'bad chunk id'
		return self
#
	def readsamps(self, nsamps):
		if self.mode[0] != 'r':
			raise Error, 'not open for reading'
		if self.nsampframes == 0:
			raise EOFError
		if self.nsampframes < nsamps:
			nsamps = self.nsampframes
		data = self.file.read(nsamps * self.nchannels * self.sampwidth)
		if len(data) < nsamps * self.nchannels * self.sampwidth:
			raise Error, 'short data'
		self.nsampframes = self.nsampframes - nsamps
		return data
#
	def init_write(self):
		if self.mode == 'w':
			self.file = open(self.filename, 'w')
		self._initialized = 0
		self._totnsampframesset = 0
		self._totnsampframes = 0
		self.nsampframes = 0
		return self
#
	def setnsamps(self, nsampframes):
		if self.mode[0] != 'w':
			raise Error, 'can only set nsamps when writing'
		self._totnsampframes = nsampframes
		self._totnsampframesset = 1
#
	def writesampsraw(self, data):
		if self.mode[0] != 'w':
			raise Error, 'not open for writing'
		if not self._initialized:
			if not self._totnsampframesset:
				try:
					self.file.seek(0)
				except RuntimeError:
					raise Error, '# frames not set before writing to pipe'
			nchannels, sampwidth, samprate = al2comm(self.nchannels, self.sampwidth, self.samprate)
			datasize = self._totnsampframes * self.nchannels * self.sampwidth
			write_form(self.file, 46 + datasize)
			write_comm(self.file, nchannels, self._totnsampframes, sampwidth, samprate)
			write_ssnd(self.file, 8 + datasize)
			self._initialized = 1
		nsamps, remain = divmod(len(data), self.nchannels * self.sampwidth)
		if remain != 0:
			raise Error, 'not writing an integral number of frames'
		if self._totnsampframesset and self.nsampframes + nsamps > self._totnsampframes:
			raise Error, 'writing more samples than allowed'
		if len(data) > 0:
			self.file.write(data)
		self.nsampframes = self.nsampframes + nsamps
#
	def writesamps(self, data):
		self.writesampsraw(data)
		if not self._totnsampframesset:
			patchsize(self.file, self.nsampframes, self.nsampframes * self.nchannels * self.sampwidth)
