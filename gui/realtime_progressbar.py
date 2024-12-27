from tkinter.ttk import Progressbar
from typing import Callable
from time import perf_counter
from .recurring_tkinter_task import ReccuringTkinterTask

class RealtimeProgressbar(Progressbar):
	
	def __init__(self, rate:float=20, delay:int=50, now:Callable[[],float]=perf_counter, *args, **kwargs):
		self.rate = rate
		self.last = None
		self.now = now
		self.task = ReccuringTkinterTask(self, delay, self.__autoincrement)
		super().__init__(*args, **kwargs)

	def __autoincrement(self):
		now = self.now()
		delta = now - self.last
		self.last = now
		amount = self.rate * delta
		self.step(amount)

	def start(self):
		self.last = self.now()
		self.task.schedule()
	
	def stop(self):
		self.last = None
		self.task.unschedule()