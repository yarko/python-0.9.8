# Module 'filewin'
# File windows, a subclass of textwin (which is a subclass of gwin)

import textwin
import builtin


# FILE WINDOW

def open_readonly(fn): # Open a file window
	fp = builtin.open(fn, 'r')
	w = textwin.open_readonly(fn, fp.read())
	w.fn = fn
	return w

def open(fn): # Open a file window
	fp = builtin.open(fn, 'r')
	w = textwin.open(fn, fp.read())
	w.fn = fn
	return w
