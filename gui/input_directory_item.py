from os import PathLike, scandir, listdir
from tkinter import ttk
from typing import Callable
from ..scan_for_audio import is_audio, is_directory
from tkinter import StringVar, IntVar
from logging import getLogger
from os.path import abspath
from .counted_progress_bar import CountedProgressbar

class InputDirectoryItem(ttk.Frame):

	def __init__(self, path:PathLike, should_scan:Callable[[PathLike],bool]=None, on_remove:Callable[['InputDirectoryItem'],None]=None, on_audio:Callable[[PathLike],None]=None, on_directory:Callable[[PathLike],None]=None, master:ttk.Widget=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input directory item')

		self.path = path
		self.should_scan = should_scan
		self.on_remove = on_remove
		self.on_audio = on_audio
		self.on_directory = on_directory
		logger.debug('setup input directory item variables')

		self.text_variable = StringVar(self, value=abspath(path))
		self.text = ttk.Entry(self, textvariable=self.text_variable, state='readonly', width=30)
		self.remove_button = ttk.Button(self, text='x', command=self.remove, width=2)
		progress_max = len(listdir(path))
		progress_variable = IntVar(self, value=0)
		self.progress = CountedProgressbar(progress_variable, progress_max, master=self)
		logger.debug('created input directory item children')

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.progress.grid(column=0, columnspan=2, row=1, sticky='EW')
		self.columnconfigure(0, weight=1)
		logger.debug('layed out input directory item')
		
		self.scanner = scandir(self.path)
		self.__schedule_next()
		logger.info(f'scanning directory: {path}')

	def __schedule_next(self):
		self.task_id = self.after(0, self.__scan)

	def __scan(self):
		logger = getLogger(__name__)

		try:
			entry = next(self.scanner)
		except StopIteration:
			self.task_id = None
			self.progress.value_variable.set(self.progress.maximum)
			logger.info(f'scan complete: {self.path}')
			self.remove()
			return
		
		if self.should_scan is None or self.should_scan(entry):
			try:
				if self.on_directory is not None and is_directory(entry):
					logger.debug(f'found another directory: {entry}')
					self.on_directory(entry)
				if self.on_audio is not None and is_audio(entry):
					logger.debug(f'found an audio file: {entry}')
					self.on_audio(entry)
			except RuntimeError as x:
				logger.error(f'failed to scan: {entry}', exc_info=x)
		else:
			logger.debug(f'not scanning: {entry}')

		self.progress.value_variable.set(self.progress.value_variable.get() + 1)
		logger.info(f'progressed scan {self.progress.value_variable.get()} / {self.progress.maximum}: {self.path}')

		self.__schedule_next()

	def remove(self):
		logger = getLogger(__name__)
		if self.on_remove:
			self.on_remove(self)
		self.destroy()
		logger.debug(f'removed input directory: {self.path}')

	def destroy(self):
		try:
			if self.task_id is not None:
				self.after_cancel(self.task_id)
		except AttributeError:
			pass
		super().destroy()