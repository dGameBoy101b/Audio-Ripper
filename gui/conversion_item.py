from concurrent.futures import Future
from logging import getLogger
from tkinter import StringVar
from tkinter.ttk import Button, Entry, Frame, Progressbar

from ..audio_copy_job import AudioCopyJob

class ConversionItem(Frame):
	def __init__(self, job:AudioCopyJob, future:Future, master=None, **kwargs):
		super().__init__(master, **kwargs)
		self.job = job
		self.future = future
		self.progress_check_id = None
		self.__create_widgets()
		self.__configure_grid()
		self.schedule_progress_check()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.path_variable = StringVar(self, self.job.args[0])
		self.path_entry = Entry(self, textvariable=self.path_variable, state='readonly')
		self.cancel_button = Button(self, text='x', command=self.destroy)
		self.progressbar = Progressbar(self, mode='indeterminate')
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.path_entry.grid(row=0, column=0, sticky='EW')
		self.cancel_button.grid(row=0, column=1)
		self.progressbar.grid(row=1, column=0, columnspan=2, sticky='EW')
		self.columnconfigure(0, weight=1)
		logger.debug(f'grid configured: {self}')

	def schedule_progress_check(self, milliseconds:int)->bool:
		if self.is_progress_check_scheduled():
			return False
		self.progress_check_id = self.after(milliseconds, self.__check_progress)
		return True

	def is_progress_check_scheduled(self)->bool:
		return self.progress_check_id is not None

	def cancel_progress_check(self):
		if not self.is_progress_check_scheduled():
			return
		self.after_cancel(self.progress_check_id)
		self.progress_check_id = None

	def __check_progress(self):
		if self.future.running():
			self.progressbar.start()
		if self.future.done():
			self.progressbar.stop()

	def destroy(self):
		self.future.cancel()
		return super().destroy()