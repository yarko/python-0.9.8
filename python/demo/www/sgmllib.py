# A parser for SGML text, using the derived class as static DTD.
# (Not much of this is compatible with real SGML -- need to fix!)


import regex
import string


# SGML parser base class -- find tags and call handler functions.
# Usage: p = SGMLParser().init(); p.feed(text); ...; p.close().
# The dtd is defined by deriving a class which defines methods
# with special names to handle tags: bgn_foo and end_foo to handle
# <foo> and </foo>, respectively, or do_foo to handle <foo> by itself.
class SGMLParser:

	# Interface -- initialize and reset this instance
	def init(self):
		self.reset()
		return self

	# Interface -- reset this instance.  Loses all unprocessed text
	def reset(self):
		self.rawtext = ''
		self.litprog = None
		self.nomoretags = 0

	# Interface -- feed some text to the parser.  Call this as
	# often as you want, with as little or as much text as you
	# want (may include '\n').  (This just saves the text, all the
	# processing is done by process() or close().)
	def feed(self, text):
		self.rawtext = self.rawtext + text

	# Interface -- handle the remaining text
	def close(self):
		self.process()

	# Interface -- parse all raw text saved so far.  Leaves no state.
	# Implied by self.close()
	def process(self):
		self.stack = []
		rawtext = self.rawtext
		self.rawtext = ''
		i = last = 0
		n = len(rawtext)
		while i < n:
			try:
				i = string.index(rawtext, '<', i)
			except string.index_error:
				break
			try:
				j = string.index(rawtext, '>', i+1) + 1
			except string.index_error:
				break
			# Now we know rawtext[i:j] == '<...>'
			if self.litprog and self.litprog.match(rawtext, i) < 0:
				i = i+1
				continue
			if last < i:
				text = rawtext[last:i]
				if self.litprog:
					self.handle_literal(text)
				else:
					text = self.replace_entities(text)
					self.handle_text(text)
			self.litprog = None
			self.handle_rawtag(rawtext[i+1:j-1])
			last = i = j
			if self.litprog:
				if self.nomoretags:
					break
		i = n
		if last < i:
			text = rawtext[last:i]
			if self.litprog:
				self.handle_literal(text)
			else:
				text = self.replace_entities(text)
				self.handle_text(text)

	# For derived classes only -- enter literal mode till end of file
	def setnomoretags(self):
		self.nomoretags = 1
		self.litprog = regex.compile('') # Not used but must be valid

	# For derived classes only -- set literal ending tag
	def setliteral(self, tag):
		re = '</'
		for c in tag:
			c, C = string.lower(c), string.upper(c)
			if c == C:
				if c in '\\.*+?[^$':
					c = '\\' + c
				re = re + c
			else:
				re = re + '[' + c + C + ']'
		re = re + '>'
		self.litprog = regex.compile(re)

	# Internal -- handle a tag (begin or end)
	def handle_rawtag(self, rawtag):
		rawtag = string.strip(rawtag)
		if rawtag[:1] == '/':
			func = self.handle_endtag
			rawtag = string.strip(rawtag[1:])
		else:
			func = self.handle_bgntag
		words = string.split(rawtag)
		if words:
			func(words[0], words[1:])

	# Internal -- handle a begin tag
	def handle_bgntag(self, tag, attrs):
		ntag = string.lower(tag)
		try:
			method = getattr(self, 'bgn_' + ntag)
		except AttributeError:
			try:
				method = getattr(self, 'do_' + ntag)
			except AttributeError:
				self.unknown_bgn(tag, attrs)
				return
			method(self.fixattrs(attrs))
			return
		self.stack.append(ntag)
		method(self.fixattrs(attrs))

	# Internal -- handle an end tag
	def handle_endtag(self, tag, attrs):
		ntag = string.lower(tag)
		try:
			method = getattr(self, 'end_' + ntag)
		except AttributeError:
			self.unknown_end(tag, attrs)
			return
		if self.stack and self.stack[-1] == ntag:
			del self.stack[-1]
		else:
			print '*** Unbalanced </' + ntag + '>'
			print '*** Stack:', self.stack
			found = None
			for i in range(len(self.stack)):
				if self.stack[i] == ntag: found = i
			if found <> None:
				del self.stack[found:]
		method(self.fixattrs(attrs))

	# Internal -- recognizer for entities (strings of the form "&word;")
	# (Some bad HTML uses "&word." instead of "&word;" -- we accept both.)
	entityprog = regex.compile('&\([a-zA-Z0-9_]+\)[.;]')

	# Definition of entities -- derived classes may override
	entitydefs = \
		{'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\''}

	# Internal -- replace entities by their definition text
	def replace_entities(self, text):
		table = self.__class__.entitydefs
		entityprog = self.__class__.entityprog
		result = []
		i = start = 0
		while entityprog.search(text, i) >= 0:
			(a, b), (c, d) = entityprog.regs[:2]
			i = b
			word = text[c:d]
			if table.has_key(word):
				if start < a: result.append(text[start:a])
				result.append(table[word])
				start = b
		if start < len(text): result.append(text[start:])
		return string.joinfields(result, '')

	# Internal -- fix the list of attributes.
	# Converts the part before '=' (if any) to lower case.
	# NB this has a side effect on the list of attributes
	def fixattrs(self, attrs):
		for i in range(len(attrs)):
			attrs[i] = self.fixattr(attrs[i])
		return attrs

	# Internal -- Fix one attribute
	def fixattr(self, attr):
		if '=' in attr:
			i = string.index(attr, '=')
			key = string.lower(attr[:i])
			value = attr[i+1:]
			if value[:1] == '"' == value[-1:]:
				value = value[1:-1]
			return key + '=' + value
		else:
			return string.lower(attr)

	# To be overridden -- handlers for text and for unknown tags
	def handle_literal(self, text): pass
	def handle_text(self, text): self.handle_literal(text)
	def unknown_bgn(self, tag, attrs): pass
	def unknown_end(self, tag, attrs): pass


# Debugging parser -- print everything that happens
class DebuggingParser(SGMLParser):
	#
	def handle_literal(self, text):
		print 'literal:', `text`
	#
	def handle_text(self, text):
		print 'text:', `text`
	#
	def _pr(self, label, tag, attrs):
		print label, `tag`,
		if attrs:
			print ' attrs:',
			for attr in attrs:
				print `attr`,
		print
	#
	def unknown_bgn(self, tag, attrs):
		self._pr('bgn tag:', tag, attrs)
	#
	def unknown_end(self, tag, attrs):
		self._pr('end tag:', tag, attrs)
