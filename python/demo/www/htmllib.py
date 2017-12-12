# A parser for HTML documents


# HTML: HyperText Markup Language; an SGML-like syntax used by WWW to
# describe hypertext documents
#
# SGML: Standard Generalized Markup Language
#
# WWW: World-Wide Web; a distributed hypertext system develped at CERN
#
# CERN: European Particle Physics Laboratory in Geneva, Switzerland


# This file is only concerned with parsing and formatting HTML
# documents, not with the other (hypertext and networking) aspects of
# the WWW project.  (It does support highlighting of anchors.)


import os
import sys
import regex
import string
import sgmllib


class HTMLParser(sgmllib.SGMLParser):

	# Copy base class entities and add some
	entitydefs = {}
	for key in sgmllib.SGMLParser.entitydefs.keys():
		entitydefs[key] = sgmllib.SGMLParser.entitydefs[key]
	entitydefs['bullet'] = '*'

	# Provided -- handlers for tags introducing literal text
	
	def bgn_listing(self, attrs):
		self.setliteral('listing')
		self.literal_bgn('listing', attrs)

	def end_listing(self, attrs):
		self.literal_end('listing', attrs)

	def bgn_xmp(self, attrs):
		self.setliteral('xmp')
		self.literal_bgn('xmp', attrs)

	def end_xmp(self, attrs):
		self.literal_end('xmp', attrs)

	def do_plaintext(self, attrs):
		self.setnomoretags()
		self.literal_bgn('plaintext', attrs)

	# To be overridden -- begin/end literal mode
	def literal_bgn(self, tag, attrs): pass
	def literal_end(self, tag, attrs): pass


# Next level of sophistication -- collect anchors, title, nextid and isindex
class CollectingParser(HTMLParser):
	#
	def init(self):
		self = HTMLParser.init(self)
		self.savetext = None
		self.nextid = ''
		self.isindex = 0
		self.title = ''
		self.inanchor = 0
		self.anchors = []
		self.anchornames = []
		self.anchortypes = []
		return self
	#
	def bgn_a(self, attrs):
		self.inanchor = 0
		href = ''
		name = ''
		type = ''
		for attr in attrs:
			if attr[:5] == 'href=':
				href = attr[5:]
			if attr[:5] == 'name=':
				name = attr[5:]
			if attr[:5] == 'type=':
				type = string.lower(attr[5:])
		if not (href or name):
			return
		self.anchors.append(href)
		self.anchornames.append(name)
		self.anchortypes.append(type)
		self.inanchor = len(self.anchors)
		if not href:
			self.inanchor = -self.inanchor
	#
	def end_a(self, attrs):
		if self.inanchor > 0:
			# Don't show anchors pointing into the current document
			if self.anchors[self.inanchor-1][:1] <> '#':
				self.handle_text('[' + `self.inanchor` + ']')
		self.inanchor = 0
	#
	def bgn_header(self, attrs): pass
	def end_header(self, attrs): pass
	#
##	def bgn_head(self, attrs): pass
##	def end_head(self, attrs): pass
	#
	def bgn_body(self, attrs): pass
	def end_body(self, attrs): pass
	#
	def do_nextid(self, attrs):
		self.nextid = attrs
	#
	def do_isindex(self, attrs):
		self.isindex = 1
	#
	def bgn_title(self, attrs):
		self.savetext = ''
	#
	def end_title(self, attrs):
		self.title = self.savetext
		self.savetext = None
	#
	def handle_text(self, text):
		if self.savetext is not None:
			self.savetext = self.savetext + text


# Formatting parser -- takes a formatter and a style sheet as arguments

# XXX The use of style sheets should change: for each tag and end tag
# there should be a style definition, and a style definition should
# encompass many more parameters: font, justification, indentation,
# vspace before, vspace after, hanging tag...

wordprog = regex.compile('[^ \t\n]*')
spaceprog = regex.compile('[ \t\n]*')

class FormattingParser(CollectingParser):

	def init(self, formatter, stylesheet):
		self = CollectingParser.init(self)
		self.fmt = formatter
		self.stl = stylesheet
		self.savetext = None
		self.compact = 0
		self.nofill = 0
		self.resetfont()
		self.setindent(self.stl.stdindent)
		return self

	def resetfont(self):
		self.fontstack = []
		self.stylestack = []
		self.fontset = self.stl.stdfontset
		self.style = ROMAN
		self.passfont()

	def passfont(self):
		font = self.fontset[self.style]
		self.fmt.setfont(font)

	def pushstyle(self, style):
		self.stylestack.append(self.style)
		self.style = min(style, len(self.fontset)-1)
		self.passfont()

	def popstyle(self):
		self.style = self.stylestack[-1]
		del self.stylestack[-1]
		self.passfont()

	def pushfontset(self, fontset, style):
		self.fontstack.append(self.fontset)
		self.fontset = fontset
		self.pushstyle(style)

	def popfontset(self):
		self.fontset = self.fontstack[-1]
		del self.fontstack[-1]
		self.popstyle()

	def flush(self):
		self.fmt.flush()

	def setindent(self, n):
		self.fmt.setleftindent(n)

	def needvspace(self, n):
		self.fmt.needvspace(n)

	def close(self):
		HTMLParser.close(self)
		self.fmt.flush()

	def handle_literal(self, text):
		lines = string.splitfields(text, '\n')
		if lines and not lines[0]: del lines[0]
		if lines and not lines[-1]: del lines[-1]
		for line in lines:
			line = string.expandtabs(line, 8)
			self.fmt.nospace = 0
			self.fmt.addword(line, 0)
			self.fmt.flush()

	def handle_text(self, text):
		if self.savetext is not None:
			self.savetext = self.savetext + text
			return
		i = 0
		n = len(text)
		while i < n:
			j = i + wordprog.match(text, i)
			word = text[i:j]
			i = j + spaceprog.match(text, j)
			self.fmt.addword(word, i-j)
			if self.nofill and '\n' in text[j:i]:
				self.fmt.flush()
				self.fmt.nospace = 0
				i = j+1
				while text[i-1] <> '\n': i = i+1

	def literal_bgn(self, tag, attrs):
		if tag == 'plaintext':
			self.flush()
		else:
			self.needvspace(1)
		self.pushfontset(self.stl.stdfontset, FIXED)
		self.setindent(self.stl.literalindent)

	def literal_end(self, tag, attrs):
		self.needvspace(1)
		self.popfontset()
		self.setindent(self.stl.stdindent)

	def bgn_title(self, attrs):
		self.flush()
		self.savetext = ''
	# NB end_title is unchanged

	def do_p(self, attrs):
		if self.compact:
			self.flush()
		else:
			self.needvspace(1)

	def bgn_h1(self, attrs):
		self.needvspace(2)
		self.setindent(self.stl.h1indent)
		self.pushfontset(self.stl.h1fontset, BOLD)
		self.fmt.setjust('c')

	def end_h1(self, attrs):
		self.popfontset()
		self.needvspace(2)
		self.setindent(self.stl.stdindent)
		self.fmt.setjust('l')

	def bgn_h2(self, attrs):
		self.needvspace(1)
		self.setindent(self.stl.h2indent)
		self.pushfontset(self.stl.h2fontset, BOLD)

	def end_h2(self, attrs):
		self.popfontset()
		self.needvspace(1)
		self.setindent(self.stl.stdindent)

	def bgn_h3(self, attrs):
		self.needvspace(1)
		self.setindent(self.stl.stdindent)
		self.pushfontset(self.stl.h3fontset, BOLD)

	def end_h3(self, attrs):
		self.popfontset()
		self.needvspace(1)
		self.setindent(self.stl.stdindent)

	def bgn_h4(self, attrs):
		self.needvspace(1)
		self.setindent(self.stl.stdindent)
		self.pushfontset(self.stl.stdfontset, BOLD)

	def end_h4(self, attrs):
		self.popfontset()
		self.needvspace(1)
		self.setindent(self.stl.stdindent)

	bgn_h5 = bgn_h4
	end_h5 = end_h4

	bgn_h6 = bgn_h5
	end_h6 = end_h5

	bgn_h7 = bgn_h6
	end_h7 = end_h6

	def bgn_ul(self, attrs):
		self.needvspace(1)
		if 'compact' in attrs:
			self.compact = 1
			self.setindent(0)
		else:
			self.setindent(self.stl.ulindent)

	bgn_dir = bgn_menu = bgn_ol = bgn_ul

	do_li = do_p

	def end_ul(self, attrs):
		self.compact = 0
		self.needvspace(1)
		self.setindent(self.stl.stdindent)

	end_dir = end_menu = end_ol = end_ul

	def bgn_dl(self, attrs):
		if 'compact' in attrs:
			self.compact = 1
		self.needvspace(1)

	def end_dl(self, attrs):
		self.compact = 0
		self.needvspace(1)
		self.setindent(self.stl.stdindent)

	def do_dt(self, attrs):
		if self.compact:
			self.flush()
		else:
			self.needvspace(1)
		self.setindent(self.stl.stdindent)

	def do_dd(self, attrs):
		self.fmt.addword('', 1)
		self.setindent(self.stl.ddindent)

	def bgn_address(self, attrs):
		self.compact = 1
		self.needvspace(1)
		self.fmt.setjust('r')

	def end_address(self, attrs):
		self.compact = 0
		self.needvspace(1)
		self.setindent(self.stl.stdindent)
		self.fmt.setjust('l')

	def bgn_typewriter(self, attrs):
		self.needvspace(1)
		self.nofill = self.nofill + 1
		self.pushstyle(FIXED)
	bgn_pre = bgn_typewriter

	def end_typewriter(self, attrs):
		self.popstyle()
		self.nofill = self.nofill - 1
		self.needvspace(1)
	end_pre = end_typewriter

	def bgn_hp1(self, attrs): self.pushstyle(ITALIC)
	def end_hp1(self, attrs): self.popstyle()

	bgn_cite = bgn_hp1
	end_cite = end_hp1

	def bgn_hp2(self, attrs): self.pushstyle(BOLD)
	def end_hp2(self, attrs): self.popstyle()

	def bgn_hp3(self, attrs): self.pushstyle(FIXED)
	def end_hp3(self, attrs): self.popstyle()

	def bgn_r(self, attrs): self.pushstyle(ROMAN)
	def end_r(self, attrs): self.popstyle()

	def bgn_dfn(self, attrs): self.pushstyle(ITALIC)
	def end_dfn(self, attrs): self.popstyle()

	def bgn_code(self, attrs): self.pushstyle(FIXED)
	def end_code(self, attrs): self.popstyle()

	bgn_samp = bgn_code
	end_samp = end_code

	bgn_file = bgn_code
	end_file = end_code

	bgn_key = bgn_code
	end_key = end_code

	bgn_kbd = bgn_code
	end_kbd = end_code

	def bgn_var(self, attrs): self.pushstyle(ITALIC)
	def end_var(self, attrs): self.popstyle()

	def unknown_bgn(self, tag, attrs):
		print '*** unknown <' + tag + '>'

	def unknown_end(self, tag, attrs):
		print '*** unknown </' + tag + '>'


# An extension of the formatting parser which formats anchors differently.
class AnchoringParser(FormattingParser):

	def bgn_a(self, attrs):
		FormattingParser.bgn_a(self, attrs)
		if self.inanchor:
			self.fmt.bgn_anchor(self.inanchor)

	def end_a(self, attrs):
		if self.inanchor:
			self.fmt.end_anchor(self.inanchor)
			self.inanchor = 0


# Style sheet -- this is never instantiated, but the attributes
# of the class object itself are used to specify fonts to be used
# for various paragraph styles.
# A font set is a non-empty list of fonts, in the order:
# [roman, italic, bold, fixed].
# When a style is not available the nearest lower style is used

ROMAN = 0
ITALIC = 1
BOLD = 2
FIXED = 3

class NullStylesheet:
	# Fonts -- none
	stdfontset = [None]
	h1fontset = [None]
	h2fontset = [None]
	h3fontset = [None]
	# Indents
	stdindent = 2
	ddindent = 25
	ulindent = 4
	h1indent = 0
	h2indent = 0
	literalindent = 0


class X11Stylesheet(NullStylesheet):
	stdfontset = [ \
		'-*-helvetica-medium-r-normal-*-*-100-100-*-*-*-*-*', \
		'-*-helvetica-medium-o-normal-*-*-100-100-*-*-*-*-*', \
		'-*-helvetica-bold-r-normal-*-*-100-100-*-*-*-*-*', \
		'-*-courier-medium-r-normal-*-*-100-100-*-*-*-*-*', \
		]
	h1fontset = [ \
		'-*-helvetica-medium-r-normal-*-*-180-100-*-*-*-*-*', \
		'-*-helvetica-medium-o-normal-*-*-180-100-*-*-*-*-*', \
		'-*-helvetica-bold-r-normal-*-*-180-100-*-*-*-*-*', \
		]
	h2fontset = [ \
		'-*-helvetica-medium-r-normal-*-*-140-100-*-*-*-*-*', \
		'-*-helvetica-medium-o-normal-*-*-140-100-*-*-*-*-*', \
		'-*-helvetica-bold-r-normal-*-*-140-100-*-*-*-*-*', \
		]
	h3fontset = [ \
		'-*-helvetica-medium-r-normal-*-*-120-100-*-*-*-*-*', \
		'-*-helvetica-medium-o-normal-*-*-120-100-*-*-*-*-*', \
		'-*-helvetica-bold-r-normal-*-*-120-100-*-*-*-*-*', \
		]
	ddindent = 40


class MacStylesheet(NullStylesheet):
	stdfontset = [ \
		('Geneva', 'p', 10), \
		('Geneva', 'i', 10), \
		('Geneva', 'b', 10), \
		('Monaco', 'p', 10), \
		]
	h1fontset = [ \
		('Geneva', 'p', 18), \
		('Geneva', 'i', 18), \
		('Geneva', 'b', 18), \
		('Monaco', 'p', 18), \
		]
	h3fontset = [ \
		('Geneva', 'p', 14), \
		('Geneva', 'i', 14), \
		('Geneva', 'b', 14), \
		('Monaco', 'p', 14), \
		]
	h3fontset = [ \
		('Geneva', 'p', 12), \
		('Geneva', 'i', 12), \
		('Geneva', 'b', 12), \
		('Monaco', 'p', 12), \
		]


if os.name == 'mac':
	StdwinStylesheet = MacStylesheet
else:
	StdwinStylesheet = X11Stylesheet


class GLStylesheet(NullStylesheet):
	stdfontset = [ \
		'Helvetica 10', \
		'Helvetica-Italic 10', \
		'Helvetica-Bold 10', \
		'Courier 10', \
		]
	h1fontset = [ \
		'Helvetica 18', \
		'Helvetica-Italic 18', \
		'Helvetica-Bold 18', \
		'Courier 18', \
		]
	h2fontset = [ \
		'Helvetica 14', \
		'Helvetica-Italic 14', \
		'Helvetica-Bold 14', \
		'Courier 14', \
		]
	h3fontset = [ \
		'Helvetica 12', \
		'Helvetica-Italic 12', \
		'Helvetica-Bold 12', \
		'Courier 12', \
		]


# Test program -- produces no output but times how long it takes
# to send a document to a null formatter, exclusive of I/O

def test():
	import fmt
	import time
	if sys.argv[1:]: file = sys.argv[1]
	else: file = 'test.html'
	data = open(file, 'r').read()
	t0 = time.millitimer()
	fmtr = fmt.WritingFormatter().init(sys.stdout, 80)
	p = FormattingParser().init(fmtr, NullStylesheet)
	p.feed(data)
	p.close()
	t1 = time.millitimer()
	print
	print '*** Formatting time:', (t1-t0) * 0.001, 'seconds.'


# Test program using stdwin

def testStdwin():
	import stdwin, fmt
	from stdwinevents import *
	if sys.argv[1:]: file = sys.argv[1]
	else: file = 'test.html'
	data = open(file, 'r').read()
	window = stdwin.open('testStdwin')
	b = None
	while 1:
		etype, ewin, edetail = stdwin.getevent()
		if etype == WE_CLOSE:
			break
		if etype == WE_SIZE:
			window.setdocsize(0, 0)
			window.setorigin(0, 0)
			window.change((0, 0), (10000, 30000)) # XXX
		if etype == WE_DRAW:
			if not b:
				b = fmt.StdwinBackEnd().init(window, 1)
				f = fmt.BaseFormatter().init(b.d, b)
				p = FormattingParser().init(f, \
							    MacStylesheet)
				p.feed(data)
				p.close()
				b.finish()
			else:
				b.redraw(edetail)
	window.close()


# Test program using GL

def testGL():
	import gl, GL, fmt
	if sys.argv[1:]: file = sys.argv[1]
	else: file = 'test.html'
	data = open(file, 'r').read()
	W, H = 600, 600
	gl.foreground()
	gl.prefsize(W, H)
	wid = gl.winopen('testGL')
	gl.ortho2(0, W, H, 0)
	gl.color(GL.WHITE)
	gl.clear()
	gl.color(GL.BLACK)
	b = fmt.GLBackEnd().init(wid)
	f = fmt.BaseFormatter().init(b.d, b)
	p = FormattingParser().init(f, GLStylesheet)
	p.feed(data)
	p.close()
	b.finish()
	#
	import time
	time.sleep(5)
