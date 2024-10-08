# Redo the `...` (representation) but with limits on most sizes.

import string

class Repr:
	def init(self):
		self.maxlevel = 6
		self.maxtuple = 6
		self.maxlist = 6
		self.maxdict = 4
		self.maxstring = 30
		self.maxlong = 40
		self.maxother = 20
		return self
	def repr(self, x):
		return self.repr1(x, self.maxlevel)
	def repr1(self, x, level):
		typename = `type(x)`[7:-2] # "<type '......'>"
		if ' ' in typename:
			parts = string.split(typename)
			typename = string.joinfields(parts, '_')
		try:
			f = eval('self.repr_' + typename)
		except AttributeError:
			s = `x`
			if len(s) > self.maxother:
				i = max(0, (self.maxother-3)/2)
				j = max(0, self.maxother-3-i)
				s = s[:i] + '...' + s[len(s)-j:]
			return s
		return f(x, level)
	def repr_tuple(self, x, level):
		n = len(x)
		if n == 0: return '()'
		if level <= 0: return '(...)'
		s = ''
		for i in range(min(n, self.maxtuple)):
			if s: s = s + ', '
			s = s + self.repr1(x[i], level-1)
		if n > self.maxtuple: s = s + ', ...'
		elif n == 1: s = s + ','
		return '(' + s + ')'
	def repr_list(self, x, level):
		n = len(x)
		if n == 0: return '[]'
		if level <= 0: return '[...]'
		s = ''
		for i in range(min(n, self.maxlist)):
			if s: s = s + ', '
			s = s + self.repr1(x[i], level-1)
		if n > self.maxlist: s = s + ', ...'
		return '[' + s + ']'
	def repr_dictionary(self, x, level):
		n = len(x)
		if n == 0: return '{}'
		if level <= 0: return '{...}'
		s = ''
		keys = x.keys()
		keys.sort()
		for i in range(min(n, self.maxdict)):
			if s: s = s + ', '
			key = keys[i]
			s = s + self.repr1(key, level-1)
			s = s + ': ' + self.repr1(x[key], level-1)
		if n > self.maxlist: s = s + ', ...'
		return '{' + s + '}'
	def repr_string(self, x, level):
		s = `x[:self.maxstring]`
		if len(s) > self.maxstring:
			i = max(0, (self.maxstring-3)/2)
			j = max(0, self.maxstring-3-i)
			s = s[:i] + '...' + s[len(s)-j:]
		return s
	def repr_long_int(self, x, level):
		s = `x` # XXX Hope this isn't too slow...
		if len(s) > self.maxlong:
			i = max(0, (self.maxlong-3)/2)
			j = max(0, self.maxlong-3-i)
			s = s[:i] + '...' + s[len(s)-j:]
		return s

aRepr = Repr().init()
repr = aRepr.repr
