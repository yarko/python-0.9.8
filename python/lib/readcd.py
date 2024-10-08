# Class interface to the CD module.

import cd, CD

Error = 'Readcd.Error'
_Stop = 'Readcd.Stop'

def _doatime(self, type, data):
	if ((data[0] * 60) + data[1]) * 75 + data[2] > self.end:
##		print 'done with list entry',`self.listindex`
		raise _Stop
	func, arg = self.callbacks[type]
	if func:
		func(arg, type, data)

def _dopnum(self, type, data):
	if data > self.end:
##		print 'done with list entry',`self.listindex`
		raise _Stop
	func, arg = self.callbacks[type]
	if func:
		func(arg, type, data)

class Readcd():
	def init(self, *arg):
		if len(arg) == 0:
			self.player = cd.open()
		elif len(arg) == 1:
			self.player = cd.open(arg[0])
		elif len(arg) == 2:
			self.player = cd.open(arg[0], arg[1])
		else:
			raise Error, 'bad init call'
		self.list = []
		self.callbacks = [(None, None)] * 8
		self.parser = cd.createparser()
		self.playing = 0
		self.end = 0
		self.status = None
		self.trackinfo = None
		return self

	def eject(self):
		self.player.eject()
		self.list = []
		self.end = 0
		self.listindex = 0
		self.status = None
		self.trackinfo = None
		if self.playing:
##			print 'stop playing from eject'
			raise _Stop

	def pmsf2msf(self, track, min, sec, frame):
		if not self.status:
			self.cachestatus()
		if track < self.status[5] or track > self.status[6]:
			raise Error, 'track number out of range'
		if not self.trackinfo:
			self.cacheinfo()
		start, total = self.trackinfo[track]
		start = ((start[0] * 60) + start[1]) * 75 + start[2]
		total = ((total[0] * 60) + total[1]) * 75 + total[2]
		block = ((min * 60) + sec) * 75 + frame
		if block > total:
			raise Error, 'out of range'
		block = start + block
		min, block = divmod(block, 75*60)
		sec, frame = divmod(block, 75)
		return min, sec, frame

	def reset(self):
		self.list = []

	def appendtrack(self, track):
		self.appendstretch(track, track)
				
	def appendstretch(self, start, end):
		if not self.status:
			self.cachestatus()
		if not start:
			start = 1
		if not end:
			end = self.status[6]
		try:
			l = len(end)
			if l == 4:
				prog, min, sec, frame = end
				if prog < self.status[5] or prog > self.status[6]:
					raise Error, 'range error'
				end = self.pmsf2msf(prog, min, sec, frame)
			elif l <> 3:
				raise Error, 'syntax error'
		except TypeError:
			if end < self.status[5] or end > self.status[6]:
				raise Error, 'range error'
		try:
			l = len(start)
			if l == 4:
				prog, min, sec, frame = start
				if prog < self.status[5] or prog > self.status[6]:
					raise Error, 'range error'
				start = self.pmsf2msf(prog, min, sec, frame)
			elif l <> 3:
				raise Error, 'syntax error'
		except TypeError:
			if start < self.status[5] or start > self.status[6]:
				raise Error, 'range error'
			if len(self.list) > 0:
				s, e = self.list[-1]
				try:
					l = len(e)
				except TypeError:
					if start == e+1:
						start = s
						del self.list[-1]
		self.list.append((start, end))

	def settracks(self, list):
		self.list = []
		for track in list:
			self.appendtrack(track)

	def setcallback(self, type, func, arg):
		if type < 0 or type >= 8:
			raise Error, 'type out of range'
		self.callbacks[type] = (func, arg)
		if self.playing:
			try:
				l = len(end)
				if type <> CD.ATIME:
					self.parser.setcallback(type, func, arg)
			except TypeError:
				if type <> CD.PNUM:
					self.parser.setcallback(type, func, arg)

	def removecallback(self, type):
		if type < 0 or type >= 8:
			raise Error, 'type out of range'
		self.callbacks[type] = (None, None)
		if self.playing:
			try:
				l = len(end)
				if type <> CD.ATIME:
					self.parser.removecallback(type)
			except TypeError:
				if type <> CD.PNUM:
					self.parser.removecallback(type)

	def gettrackinfo(self, *arg):
		if not self.status:
			self.cachestatus()
		if not self.trackinfo:
			self.cacheinfo()
		if len(arg) == 0:
			return self.trackinfo[self.status[5]:self.status[6]+1]
		result = []
		for i in arg:
			if i < self.status[5] or i > self.status[6]:
				raise Error, 'range error'
			result.append(self.trackinfo[i])
		return result

	def cacheinfo(self):
		if not self.status:
			self.cachestatus()
		self.trackinfo = []
		for i in range(self.status[5]):
			self.trackinfo.append(None)
		for i in range(self.status[5], self.status[6]+1):
			self.trackinfo.append(self.player.gettrackinfo(i))

	def cachestatus(self):
		self.status = self.player.getstatus()
		if self.status[0] == CD.NODISC:
			self.status = None
			raise Error, 'no disc in player'

	def getstatus(self):
		return self.player.getstatus()

	def play(self):
		if not self.status:
			self.cachestatus()
		size = self.player.bestreadsize()
		self.listindex = 0
		self.playing = 0
		for i in range(8):
			func, arg = self.callbacks[i]
			if func:
				self.parser.setcallback(i, func, arg)
			else:
				self.parser.removecallback(i)
		if len(self.list) == 0:
			for i in range(self.status[5], self.status[6]+1):
				self.appendtrack(i)
		while 1:
			if not self.playing:
				if self.listindex >= len(self.list):
					return
				start, end = self.list[self.listindex]
##				print 'starting with',`(start, end)`
				try:
					min, sec, frame = start
					dummy = self.player.seek(min, sec, frame)
				except TypeError:
					dummy = self.player.seektrack(start)
				try:
					min, sec, frame = end
					self.parser.setcallback(CD.ATIME, _doatime, self)
					self.end = (min * 60 + sec) * 75 + frame
					func, arg = self.callbacks[CD.PNUM]
					if func:
						self.parser.setcallback(CD.PNUM, func, arg)
					else:
						self.parser.removecallback(CD.PNUM)
				except TypeError:
					self.parser.setcallback(CD.PNUM, _dopnum, self)
					self.end = end
					func, arg = self.callbacks[CD.ATIME]
					if func:
						self.parser.setcallback(CD.ATIME, func, arg)
					else:
						self.parser.removecallback(CD.ATIME)
				self.playing = 1
			data = self.player.readda(size)
			if data == '':
				self.playing = 0
				self.listindex = self.listindex + 1
				continue
			try:
				self.parser.parseframe(data)
			except _Stop:
				self.playing = 0
				self.listindex = self.listindex + 1
