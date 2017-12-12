# Parse a timezone specification.
# XXX Unfinished.
# XXX Only the typical form "XXXhhYYY;ddd/hh,ddd/hh" is currently supported.

tzpat = '^\([A-Z][A-Z][A-Z]\)\([-+]?[0-9]+\)\([A-Z][A-Z][A-Z]\);' + \
	  '\([0-9]+\)/\([0-9]+\),\([0-9]+\)/\([0-9]+\)$'

tzprog = None

def tzparse(tzstr):
	global tzprog
	if tzprog == None:
		import regex
		tzprog = regex.compile(tzpat)
	if not tzprog.match(tzstr):
		raise ValueError, 'not the TZ syntax I understand'
	regs = tzprog.regs
	subs = []
	for i in range(1, 8):
		a, b = regs[i]
		subs.append(tzstr[a:b])
	for i in (1, 3, 4, 5, 6):
		subs[i] = eval(subs[i])
	[tzname, delta, dstname, daystart, hourstart, dayend, hourend] = subs
	return (tzname, delta, dstname, daystart, hourstart, dayend, hourend)

def tzlocaltime(time, params):
	import calendar
	(tzname, delta, dstname, daystart, hourstart, dayend, hourend) = params
	year, month, days, hours, mins, secs, yday, wday = \
		calendar.gmtime(time - delta*3600)
	if (daystart, hourstart) <= (yday+1, hours) < (dayend, hourend):
		tzname = dstname
		hours = hours + 1
	return year, month, days, hours, mins, secs, yday, wday, tzname

def tzset():
	global tzparams, timezone, altzone, daylight, tzname
	import os
	tzstr = os.environ['TZ']
	tzparams = tzparse(tzstr)
	timezone = tzparams[1] * 3600
	altzone = timezone + 3600
	daylight = 1
	tzname = tzparams[0], tzparams[2]

def isdst(time):
	import calendar
	(tzname, delta, dstname, daystart, hourstart, dayend, hourend) = \
		tzparams
	year, month, days, hours, mins, secs, yday, wday = \
		calendar.gmtime(time - delta*3600)
	return (daystart, hourstart) <= (yday+1, hours) < (dayend, hourend)

tzset()

def localtime(time):
	return tzlocaltime(time, tzparams)

def test():
	from calendar import asctime, gmtime
	import time, sys
	now = time.time()
	x = localtime(now)
	print 'now =', now, '=', asctime(x[:-1]), x[-1]
	now = now - now % (24*3600)
	if sys.argv[1:]: now = now + eval(sys.argv[1])
	x = gmtime(now)
	print 'gmtime =', now, '=', asctime(x), 'yday =', x[-2]
	jan1 = now - x[-2]*24*3600
	x = localtime(jan1)
	print 'jan1 =', jan1, '=', asctime(x[:-1]), x[-1]
	for d in range(85, 95) + range(265, 275):
		t = jan1 + d*24*3600
		x = localtime(t)
		print 'd =', d, 't =', t, '=', asctime(x[:-1]), x[-1]
