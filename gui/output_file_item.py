from concurrent.futures import Future
from logging import getLogger
from os import PathLike, fsdecode
from tkinter import DoubleVar, Misc, StringVar
from tkinter.ttk import Button, Entry, Frame

from .recurring_tkinter_task import ReccuringTkinterTask
from .realtime_progressbar import RealtimeProgressbar

StrPath = PathLike|str

class OutputFileItem(Frame):
	def __init__(self, path:StrPath, future:Future|None=None, master:Misc|None=None, **kwargs):
		super().__init__(master, **kwargs)
		self.future = None
		self.check_progress_task = ReccuringTkinterTask(self, 'idle', self.__check_progress)
		self.__create_widgets(path)
		self.__configure_grid()
		if future is not None:
			self.started(future)

	def __create_widgets(self, path:StrPath):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.path_variable = StringVar(self, fsdecode(path))
		self.path_entry = Entry(self, textvariable=self.path_variable, state='readonly')
		self.progress_variable = DoubleVar(self)
		self.progress_bar = RealtimeProgressbar(rate=200, master=self, mode='indeterminate', variable=self.progress_variable, )
		self.destory_button = Button(master=self, command=self.destroy, text='x', width=2)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.path_entry.grid(row=0, column=0, sticky='EW')
		self.destory_button.grid(row=0, column=1)
		self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='EW')
		if self.future is None:
			self.destory_button.grid_remove()
			self.progress_bar.grid_remove()
			logger.debug(f'configuring grid in preview mode: {self}')
		self.columnconfigure(0, weight=1)
		logger.debug(f'grid configured: {self}')

	def started(self, future:Future):
		logger = getLogger(__name__)
		if self.future is not None:
			logger.warning(f'overwriting output future: {self}')
			self.future.cancel()
		self.future = future
		self.destory_button.grid()
		self.progress_bar.grid()
		self.progress_bar.configure(mode='indeterminate')
		self.progress_bar.start()
		self.check_progress_task.schedule()
		logger.info(f'rip job started: {self.path_variable.get()}')

	def __check_progress(self):
		logger = getLogger(__name__)
		logger.debug(f'checking rip progress... {self.path_variable.get()}')
		if self.future is None:
			logger.warning(f'checked progress of unstarted job: {self.path_variable.get()}')
			self.check_progress_task.unschedule()
			return
		if self.future.cancelled():
			logger.info(f'rip job cancelled: {self.path_variable.get()}')
			self.check_progress_task.unschedule()
			self.progress_bar.config(mode='determinate')
			self.progress_bar.stop()
			self.progress_variable.set(0)
			return
		if self.future.done():
			self.check_progress_task.unschedule()
			self.progress_bar.stop()
			self.destory_button.grid_remove()
			exception = self.future.exception(timeout=0)
			self.progress_bar.config(mode='determinate')
			if exception is None:
				logger.info(f'rip job completed: {self.path_variable.get()}')
				self.progress_variable.set(100)
			else:
				logger.error(f'rip job failed: {self.path_variable.get()}', exc_info=exception)
				self.progress_variable.set(0)
			return
		logger.debug(f'no progress found: {self.path_variable.get()}')

	def destory(self):
		logger = getLogger(__name__)
		self.check_progress_task.unschedule()
		self.progress_bar.stop()
		if self.future is not None and not self.future.done():
			if not self.future.cancel():
				logger.warning(f'failed to cancel running rip job: {self.path_variable.get()}')