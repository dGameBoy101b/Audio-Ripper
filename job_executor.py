from concurrent.futures import Executor, Future
from dataclasses import dataclass
from queue import Queue
from typing import Callable

@dataclass(frozen=True)
class Job:
	function:Callable
	args:tuple[any] = tuple()
	kwargs:dict[any] = dict()

	def execute(self):
		self.function(*self.args, **self.kwargs)

class JobExecutor:
	def __init__(self, executor:Executor, jobs:Queue[Job]=None):
		self.executor = executor
		if isinstance(jobs, Queue):
			self.jobs = jobs
		else:
			self.jobs = Queue()
			if jobs is not None:
				for job in jobs:
					self.jobs.put(job)

	def __on_job_done(self, future:Future):
		self.jobs.task_done()

	def start_jobs(self, count:int|None=None)->list[Future]:
		futures = list()
		while not self.jobs.empty() and (count is None or count > 0):
			job = self.jobs.get()
			future = self.executor.submit(job.execute)
			future.add_done_callback(self.__on_job_done)
			futures.append(future)
		return futures
	
	def __del__(self):
		self.executor.shutdown(cancel_futures=True)
		#self.jobs.shutdown(immediate=True)