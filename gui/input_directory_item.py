from os import PathLike, scandir, listdir
from tkinter import ttk
from tkinter import StringVar, IntVar
from logging import getLogger
from os.path import abspath
from .counted_progress_bar import CountedProgressbar

StrPath = PathLike|str

class InputDirectoryItem(ttk.Frame):

	def __init__(self, path:StrPath, master:ttk.Widget|None=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input directory item')

		self.text_variable = StringVar(self, value=abspath(path))
		self.text = ttk.Entry(self, textvariable=self.text_variable, state='readonly', width=30)
		self.remove_button = ttk.Button(self, text='x', command=self.destroy, width=2)
		progress_max = len(listdir(path))
		self.progress_variable = IntVar(self, value=0)
		self.progress = CountedProgressbar(self.progress_variable, progress_max, master=self)
		logger.debug('created input directory item children')

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.progress.grid(column=0, columnspan=2, row=1, sticky='EW')
		self.columnconfigure(0, weight=1)
		logger.debug('layed out input directory item')
		
		self.scanner = scandir(path)
		self.task_id = None
		logger.info(f'queued input directory scan: {abspath(path)}')

	def increment_progress(self):
		logger = getLogger(__name__)
		value = self.progress_variable.get()+1
		self.progress_variable.set(value)
		logger.debug(f'progress incremented on directory to {value} / {self.progress.maximum}: {abspath(self.get())}')

	def get(self)->StrPath:
		return self.text_variable.get()
