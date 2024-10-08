# This file implements a class which forms an interface to the .cdplayerrc
# file that is maintained by SGI's cdplayer program.
#
# Usage is as follows:
#
# import readcd
# r = readcd.Readcd().init()
# c = Cdplayer().init(r.gettrackinfo())
#
# Now you can use c.artist, c.title and c.track[trackno] (where trackno
# starts at 1).  When the CD is not recognized, all values will be the empty
# string.
# It is also possible to set the above mentioned variables to new values.
# You can then use c.write() to write out the changed values to the
# .cdplayerrc file.

cdplayerrc = '.cdplayerrc'

class Cdplayer():
	def init(self, tracklist):
		import string
		self.artist = ''
		self.title = ''
		if type(tracklist) == type(''):
			t = []
			for i in range(2, len(tracklist), 4):
				t.append((None, \
					  (string.atoi(tracklist[i:i+2]), \
					   string.atoi(tracklist[i+2:i+4]))))
			tracklist = t
		self.track = [None] + [''] * len(tracklist)
		self.id = 'd' + string.zfill(len(tracklist), 2)
		for track in tracklist:
			start, length = track
			self.id = self.id + string.zfill(length[0], 2) + \
				  string.zfill(length[1], 2)
		try:
			import posix
			f = open(posix.environ['HOME'] + '/' + cdplayerrc, 'r')
		except IOError:
			return self
		import regex
		reg = regex.compile('^\\([^:]*\\):\t\\(.*\\)')
		s = self.id + '.'
		l = len(s)
		while 1:
			line = f.readline()
			if line == '':
				break
			if line[:l] == s:
				line = line[l:]
				if reg.match(line) == -1:
					print 'syntax error in ~/' + cdplayerrc
					continue
				name = line[reg.regs[1][0]:reg.regs[1][1]]
				value = line[reg.regs[2][0]:reg.regs[2][1]]
				if name == 'title':
					self.title = value
				elif name == 'artist':
					self.artist = value
				elif name[:5] == 'track':
					trackno = string.atoi(name[6:])
					self.track[trackno] = value
		f.close()
		return self

	def write(self):
		import posix
		filename = posix.environ['HOME'] + '/' + cdplayerrc
		try:
			old = open(filename, 'r')
		except IOError:
			old = open('/dev/null', 'r')
		new = open(filename + '.new', 'w')
		s = self.id + '.'
		l = len(s)
		while 1:
			line = old.readline()
			if line == '':
				break
			if line[:l] <> s:
				new.write(line)
		new.write(self.id + '.title:\t' + self.title + '\n')
		new.write(self.id + '.artist:\t' + self.artist + '\n')
		for i in range(1, len(self.track)):
			new.write(self.id + '.track.' + `i` + ':\t' + \
				  self.track[i] + '\n')
		old.close()
		new.close()
		posix.rename(filename + '.new', filename)
