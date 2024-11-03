from os import PathLike, scandir, listdir
from tkinter import ttk
from typing import Callable
from tkinter import StringVar, IntVar
from logging import getLogger
from os.path import abspath
from .counted_progress_bar import CountedProgressbar

class InputDirectoryItem(ttk.Frame):

	def __init__(self, path:PathLike, master:ttk.Widget=None, *, on_remove:Callable[['InputDirectoryItem'],None]=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input directory item')

		self.path = path
		self.on_remove = on_remove
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
		self.task_id = None
		logger.info(f'queued input directory scan: {path}')

	def remove(self):
		logger = getLogger(__name__)
		if self.on_remove:
			self.on_remove(self)
		self.destroy()
		logger.debug(f'removed input directory: {self.path}')

	def increment_progress(self):
		logger = getLogger(__name__)
		self.progress.value_variable.set(self.progress.value_variable.get()+1)
		logger.debug(f'progress incremented on directory: {self.path}')
