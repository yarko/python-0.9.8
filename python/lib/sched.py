# Module sched -- a generally useful event scheduler class

# Each instance of this class manages its own queue.
# No multi-threading is implied; you are supposed to hack that
# yourself, or use a single instance per application.
#
# Each instance is parametrized with two functions, one that is
# supposed to return the current time, one that is supposed to
# implement a delay.  You can implement fine- or course-grained
# real-time scheduling by substituting time and sleep or millitimer
# and millisleep from the built-in module time, or you can implement
# simulated time by writing your own functions.  This can also be
# used to integrate scheduling with STDWIN events; the delay function
# is allowed to modify the queue.  Time can be expressed as
# integers or floating point numbers, as long as it is consistent.

# Events are specified by tuples (time, priority, action, argument).
# As in UNIX, lower priority numbers mean higher priority; in this
# way the queue can be maintained fully sorted.  Execution of the
# event means calling the action function, passing it the argument.
# Remember that in Python, multiple function arguments can be packed
# in a tuple.   The action function may be an instance method so it
# has another way to reference private data (besides global variables).
# Parameterless functions or methods cannot be used, however.

# XXX The timefunc and delayfunc should have been defined as methods
# XXX so you can define new kinds of schedulers using subclassing
# XXX instead of having to define a module or class just to hold
# XXX the global state of your particular time and delay functtions.

import bisect

class scheduler:
	#
	# Initialize a new instance, passing the time and delay functions
	#
	def init(self, timefunc, delayfunc):
		self.queue = []
		self.timefunc = timefunc
		self.delayfunc = delayfunc
		return self
	#
	# Enter a new event in the queue at an absolute time.
	# Returns an ID for the event which can be used
	# to remove it, if necessary.
	#
	def enterabs(self, time, priority, action, argument):
		event = time, priority, action, argument
		bisect.insort(self.queue, event)
		return event # The ID
	#
	# A variant that specifies the time as a relative time.
	# This is actually the more commonly used interface.
	#
	def enter(self, delay, priority, action, argument):
		time = self.timefunc() + delay
		return self.enterabs(time, priority, action, argument)
	#
	# Remove an event from the queue.
	# This must be presented the ID as returned by enter().
	# If the event is not in the queue, this raises RuntimeError.
	#
	def cancel(self, event):
		self.queue.remove(event)
	#
	# Check whether the queue is empty.
	#
	def empty(self):
		return len(self.queue) == 0
	#
	# Run: execute events until the queue is empty.
	#
	# When there is a positive delay until the first event, the
	# delay function is called and the event is left in the queue;
	# otherwise, the event is removed from the queue and executed
	# (its action function is called, passing it the argument).
	# If the delay function returns prematurely, it is simply
	# restarted.
	#
	# It is legal for both the delay function and the action
	# function to to modify the queue or to raise an exception;
	# exceptions are not caught but the scheduler's state
	# remains well-defined so run() may be called again.
	#
	# A questionably hack is added to allow other threads to run:
	# just after an event is executed, a delay of 0 is executed,
	# to avoid monopolizing the CPU when other threads are also
	# runnable.
	#
	def run(self):
		q = self.queue
		while q:
			time, priority, action, argument = q[0]
			now = self.timefunc()
			if now < time:
				self.delayfunc(time - now)
			else:
				del q[0]
				void = apply(action, argument)
				self.delayfunc(0) # Let other threads run
	#
