from logging import getLogger
from os import PathLike, fspath
from os.path import isdir, abspath
from tkinter.ttk import Labelframe, Label, Entry, Button
from tkinter import StringVar
from tkinter.filedialog import askdirectory

from .conversions_frame import ConversionsFrame

class OutputFrame(Labelframe):

	def __init__(self, master=None):
		super().__init__(master, text='Output')
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.directory_variable = StringVar(self)
		self.directory_label = Label(self, text='Output Directory')
		self.directory_entry = Entry(self, justify='left', textvariable=self.directory_variable)
		self.directory_button = Button(self, text='Browse...', command=self.set_directory)
		self.rip_button = Button(self, text='Start Rip', command=self.start_rip)
		self.conversions_frame = ConversionsFrame(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.directory_label.grid(row=0, column=0)
		self.directory_entry.grid(row=0, column=1, sticky='EW')
		self.directory_button.grid(row=0, column=2)
		self.rip_button.grid(row=1, column=0, columnspan=3, sticky='EW')
		self.conversions_frame.grid(row=2, column=0, columnspan=3, sticky='NSEW')
		self.columnconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		logger.debug(f'grid configured: {self}')

	def set_directory(self, directory:PathLike=None)->bool:
		logger = getLogger(__name__)

		if directory is None:
			directory = askdirectory(title="Output Directory")
			if directory == '':
				logger.info('no output directory selected')
				return False
		
		if not isdir(directory):
			logger.warning(f'non-directory given as output directory: {fspath(directory)}')
			return False
		
		self.directory_variable.set(abspath(directory))
		logger.info(f'set output directory: {fspath(directory)}')
		return True

	def start_rip(self):
		logger = getLogger(__name__)
		logger.info('starting rip...')
		logger.info('rip complete')