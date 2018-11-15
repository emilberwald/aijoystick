from multiprocessing import Process, Queue


class Call:
	def __init__(self, function):
		assert function
		self.queue = Queue()
		self.function = function

	@staticmethod
	def _wrap_function(func, queue, args, kwargs):
		queue.put(func(*args, **kwargs))

	def __call__(self, *args, **kwargs):
		p = Process(
		    target=self._wrap_function,
		    args=[self.function, self.queue, args, kwargs])
		p.start()
		ret = self.queue.get()
		p.join()
		return ret
