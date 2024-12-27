from concurrent.futures import Future
from logging import getLogger
from os import PathLike
from tkinter import DoubleVar, Misc, StringVar
from tkinter.ttk import Entry, Frame

from .recurring_tkinter_task import ReccuringTkinterTask
from .realtime_progressbar import RealtimeProgressbar

class OutputFileItem(Frame):
	def __init__(self, path:PathLike, master:Misc=None, **kwargs):
		super().__init__(master, **kwargs)
		self.future = None
		self.check_progress_task = ReccuringTkinterTask(self, 'idle', self.__check_progress)
		self.__create_widgets(path)
		self.__configure_grid()

	def __create_widgets(self, path:PathLike):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.path_variable = StringVar(self, path)
		self.path_entry = Entry(self, textvariable=self.path_variable, state='readonly')
		self.progress_variable = DoubleVar(self)
		self.progress_bar = RealtimeProgressbar(self, mode='indeterminate', variable=self.progress_variable)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.path_entry.grid(row=0, column=0, sticky='EW')
		self.progress_bar.grid(row=1, column=0, sticky='EW')
		logger.debug(f'grid configured: {self}')

	def started(self, future:Future):
		self.future = future
		self.progress_bar.configure(mode='indeterminate')
		self.progress_bar.start()
		self.check_progress_task.schedule()

	def __check_progress(self):
		logger = getLogger(__name__)
		logger.debug(f'checking rip progress... {self}')
		if self.future is None:
			logger.warning(f'checked progress of unstarted job: {self}')
			self.check_progress_task.unschedule()
			return
		if self.future.cancelled():
			logger.info(f'rip job cancelled: {self}')
			self.check_progress_task.unschedule()
			self.progress_bar.config(mode='determinate')
			self.progress_bar.stop()
			self.progress_variable.set(0)
			return
		if self.future.done():
			logger.info(f'rip job completed: {self}')
			self.check_progress_task.unschedule()
			self.progress_bar.stop()
			self.progress_bar.config(mode='determinate')
			self.progress_variable.set(100)
			return
		logger.debug(f'no progress found: {self}')
