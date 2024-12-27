from concurrent.futures import BrokenExecutor, Executor
from logging import getLogger
from typing import Any, Callable


class ResiliantExecutor(Executor):
	'''An executor wrapper that recreates its underlying executor when broken'''

	def __init__(self, executor_factory:Callable[...,Executor], *args, **kwargs):
		self.executor_factory = executor_factory
		self.args = args
		self.kwargs = kwargs
		self.executor = self.create_executor()

	def create_executor(self)->Executor:
		return self.executor_factory(*self.args, **self.kwargs)

	def revive(self):
		logger = getLogger(__name__)
		old = self.executor
		try:
			old.shutdown(wait=False, cancel_futures=True)
		except BaseException as x:
			logger.error(f'Failed to shutdown old executor while reviving', exc_info=x)
		finally:
			self.executor = self.create_executor()
			logger.warning(f'executor revived: {old} -> {self.executor}')

	def __try(self, fn:Callable[[],Any])->Any:
		try:
			return fn()
		except BrokenExecutor:
			self.revive()
			return fn()

	def submit(self, fn, /, *args, **kwargs):
		return self.__try(lambda: self.executor.submit(fn, *args, **kwargs))
		
	def map(self, fn, *iterables, timeout=None, chunksize=1):
		return self.__try(lambda: self.executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize))
		
	def shutdown(self, wait = True, *, cancel_futures = False):
		return self.__try(lambda: self.executor.shutdown(wait, cancel_futures=cancel_futures))
	
	def __enter__(self):
		return self.__try(lambda: self.executor.__enter__())
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		return self.__try(lambda: self.executor.__exit__(exc_type, exc_val, exc_tb))