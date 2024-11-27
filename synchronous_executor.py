from concurrent.futures import Executor, Future

class SynchronousExecutor(Executor):
	def submit(self, fn, /, *args, **kwargs)->Future:
		future = Future()
		if future.set_running_or_notify_cancel():
			try:
				future.set_result(fn(*args, **kwargs))
			except BaseException as x:
				future.set_exception(x)
		return future
	