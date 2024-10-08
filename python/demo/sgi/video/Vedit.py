#! /ufs/guido/bin/sgi/python

# Edit CMIF movies interactively -- copy one or more files to an output file


# XXX To do:
#
# - convert between formats (grey, rgb, rgb8, ...)
# - change size
# - cut out a given area of the image
# - change time base (a la Vtime)


import sys
import os
import gl, GL, DEVICE
import fl, FL
import flp
import Viewer
import getopt
import string


def main():
	qsize = 40
	opts, args = getopt.getopt(sys.argv[1:], 'q:')
	for o, a in opts:
		if o == '-q':
			qsize = string.atoi(a)
	ed = Editor().init(qsize)
	if args[0:]:
		ed.open_input(args[0])
	if args[1:]:
		ed.open_output(args[1])
	while 1:
		dummy = fl.do_forms()


class Editor:

	def init(self, qsize):
		self.qsize = qsize
		self.vin = None
		self.vout = None
		self.ifile = ''
		self.ofile = ''
		formdef = flp.parse_form('VeditForm', 'form')
		flp.create_full_form(self, formdef)
		self.form.show_form(FL.PLACE_SIZE, FL.TRUE, 'Vedit')
		fl.set_event_call_back(self.do_event)
		return self

	def do_event(self, dev, val):
		if dev == DEVICE.REDRAW:
			if self.vin:
				self.vin.redraw(val)
			if self.vout:
				self.vout.redraw(val)


	def iocheck(self):
		self.msg('')
		if self.vin == None and self.vout == None:
			self.err('Please open input and output files first')
			return 0
		return self.icheck() and self.ocheck()

	def icheck(self):
		self.msg('')
		if self.vin == None:
			self.err('Please open an input file first')
			return 0
		return 1

	def ocheck(self):
		self.msg('')
		if self.vout == None:
			self.err('Please open an output file first')
			return 0
		return 1


	def cb_in_new(self, *args):
		self.msg('')
		hd, tl = os.path.split(self.ifile)
		filename = fl.file_selector('Input video file', hd, '', tl)
		if not filename: return
		self.open_input(filename)

	def cb_in_close(self, *args):
		self.msg('')
		self.close_input()

	def cb_in_skip(self, *args):
		if not self.icheck(): return
		if not self.vin.get(): self.err('End of input file')
		self.ishow()

	def cb_in_back(self, *args):
		if not self.icheck(): return
		if not self.vin.backup(): self.err('Input buffer exhausted')
		self.ishow()

	def cb_in_rewind(self, *args):
		if not self.icheck(): return
		self.vin.rewind()
		self.ishow()


	def cb_copy(self, *args):
		if not self.iocheck(): return
		data = self.vin.get()
		if not data:
			self.err('End of input file')
			self.ishow()
			return
		if self.vout.getinfo() <> self.vin.getinfo():
			print 'Copying info...'
			self.vout.setinfo(self.vin.getinfo())
		self.vout.put(data)
		self.oshow()
		self.ishow()

	def cb_uncopy(self, *args):
		if not self.iocheck(): return
		if not self.vout.backup():
			self.err('Output buffer exhausted')
			return
		self.oshow()
		if not self.vin.backup():
			self.err('Input buffer exhausted')
			return
		self.ishow()


	def cb_out_new(self, *args):
		self.msg('')
		hd, tl = os.path.split(self.ofile)
		filename = fl.file_selector('Output video file', hd, '', tl)
		if not filename: return
		self.open_output(filename)

	def cb_out_close(self, *args):
		self.msg('')
		self.close_output()

	def cb_out_skip(self, *args):
		if not self.ocheck(): return
		if not self.vout.forward(): self.err('Output buffer exhausted')
		self.oshow()
		
	def cb_out_back(self, *args):
		if not self.ocheck(): return
		if not self.vout.backup(): self.err('Output buffer exhausted')
		self.oshow()

	def cb_out_rewind(self, *args):
		if not self.ocheck(): return
		self.vout.rewind()
		self.oshow()


	def cb_quit(self, *args):
		self.close_input()
		self.close_output()
		sys.exit(0)


	def open_input(self, filename):
		self.ifile = filename
		basename = os.path.split(filename)[1]
		title = 'in: ' + basename
		try:
			vin = Viewer.InputViewer().init(filename, \
				title, self.qsize)
		except:
			self.err('Can\'t open input file', filename)
			return
		self.close_input()
		self.vin = vin
		self.in_file.label = basename
		self.ishow()

	def close_input(self):
		if self.vin:
			self.msg('Closing input file...')
			self.vin.close()
		self.msg('')
		self.vin = None
		self.in_file.label = '(none)'
		self.format('in')

	def ishow(self):
		self.vin.show()
		self.format('in')

	def open_output(self, filename):
		self.ofile = filename
		basename = os.path.split(filename)[1]
		title = 'out: ' + basename
		try:
			vout = Viewer.OutputViewer().init(filename, \
				title, self.qsize)
		except:
			self.err('Can\'t open output file', filename)
			return
		self.close_output()
		self.vout = vout
		self.out_file.label = basename
		if self.vin:
			self.vout.setinfo(self.vin.getinfo())
			self.oshow()

	def close_output(self):
		if self.vout:
			self.msg('Closing output file...')
			self.vout.close()
		self.msg('')
		self.vout = None
		self.out_file.label = '(none)'
		self.format('out')

	def oshow(self):
		self.vout.show()
		self.format('out')


	def msg(self, *args):
		str = string.strip(string.join(args))
		self.msg_area.label = str

	def err(self, *args):
		gl.ringbell()
		apply(self.msg, args)

	def format(self, io):
		v = getattr(self, 'v' + io)
		if v == None:
			left = right = pos = 0
		else:
			left, right = v.qsizes()
			pos = v.tell()
			left = pos - left
			right = pos + right
		getattr(self, io + '_info1').label = `left`
		getattr(self, io + '_info2').label = `pos`
		getattr(self, io + '_info3').label = `right`


try:
	main()
except KeyboardInterrupt:
	print '[Interrupt]'
