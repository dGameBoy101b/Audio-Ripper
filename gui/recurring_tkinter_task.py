from logging import getLogger
from tkinter import Misc
from typing import Callable, Literal

class ReccuringTkinterTask():
	def __init__(self, widget:Misc, delay_ms:int|Literal['idle']='idle', callback:Callable=None):
		self.__id = None
		self.widget = widget
		self.delay_ms = delay_ms
		self.callback = callback

	def is_scheduled(self)->bool:
		return self.__id is not None

	def schedule(self):
		logger = getLogger(__name__)
		if self.is_scheduled():
			logger.warning(f'recurring task already scheduled on {self.widget}: {self.callback}')
			return
		self.__id = self.widget.after(self.delay_ms, self.__run)
		logger.info(f'scheduled task recurring every {self.delay_ms} on {self.widget}: {self.callback}')

	def unschedule(self):
		logger = getLogger(__name__)
		if not self.is_scheduled():
			return
		self.widget.after_cancel(self.__id)
		self.__id = None
		logger.info(f'unscheduled recurring task on {self.widget}: {self.callback}')

	def __run(self):
		logger = getLogger(__name__)
		self.callback()
		logger.info(f'run recurring task on {self.widget}: {self.callback}')
		if self.__id is not None:
			self.__id = None
			self.schedule()
		