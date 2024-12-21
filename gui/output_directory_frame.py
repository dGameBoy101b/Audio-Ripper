from logging import getLogger
from os import PathLike, fspath
from os.path import isdir
from posixpath import abspath
from tkinter import StringVar
from tkinter.ttk import Button, Entry, Frame, Label
from tkinter.filedialog import askdirectory


class OutputDirectoryFrame(Frame):
	
	def __init__(self, master=None, **kwargs):
		super().__init__(master, **kwargs)
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.variable = StringVar(self)
		self.label = Label(self, text='Output Directory: ')
		self.entry = Entry(self, justify='left', textvariable=self.variable)
		self.browse_button = Button(self, text='Browse...', command=self.ask)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.label.grid(row=0, column=0)
		self.entry.grid(row=0, column=1, sticky='EW')
		self.browse_button.grid(row=0, column=2)
		self.columnconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')

	def ask(self)->bool:
		logger = getLogger(__name__)
		directory = askdirectory(title="Output Directory")
		if directory == '':
			logger.info('no output directory selected')
			return False
		try:
			self.set(directory)
		except BaseException as x:
			logger.warning(f'user selected invalid out directory: {directory}', exc_info=x)
			return False
		return True

	def set(self, directory:PathLike):
		logger = getLogger(__name__)
		if not isdir(directory):
			raise ValueError(f'non-directory given as output directory: {fspath(directory)}')
		self.variable.set(abspath(directory))
		logger.info(f'set output directory: {fspath(directory)}')
	
	def get(self)->PathLike:
		return self.variable.get()