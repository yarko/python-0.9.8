from time import millitimer
from scanner import scan
f = open('../wais-questions/Fetch', 'r')
class F:
	def init(self, f):
		self.f = f
		return self
	def readline(self):
		return self.f.read()
def nop(s): pass
def show(s): print repr(s)
fp = F().init(f)
wsp = ' \t\n\f'
token = '[()#]\|[^()#"; \t\n\r\f]+\|"\(\\\\.\|[^\\"]\)*"'
t0 = millitimer()
try:
	scan(fp, wsp, token, nop)
except EOFError:
	pass
t1 = millitimer()
print (t1-t0)*0.001, 'sec'
f.seek(0)
scan(fp, wsp, token, show)
