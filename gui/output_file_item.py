from logging import getLogger
from os import PathLike
from tkinter import Misc, StringVar
from tkinter.ttk import Entry, Frame, Progressbar

class OutputFileItem(Frame):
	def __init__(self, path:PathLike, master:Misc=None, **kwargs):
		super().__init__(master, **kwargs)
		self.__create_widgets(path)
		self.__configure_grid()

	def __create_widgets(self, path:PathLike):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.path_variable = StringVar(self, path)
		self.path_entry = Entry(self, textvariable=self.path_variable, state='readonly')
		self.progress_bar = Progressbar(self, mode='indeterminate')
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.path_entry.grid(row=0, column=0, sticky='EW')
		self.progress_bar.grid(row=1, column=0, stiky='EW')
		logger.debug(f'grid configured: {self}')

	def started(self):
		self.progress_bar.start()

	def completed(self):
		self.progress_bar.stop()