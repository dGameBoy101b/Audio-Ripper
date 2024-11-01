from os import PathLike
from tkinter import ttk
from tkinter import filedialog
from ..scan_for_audio import is_audio
from ..scan_for_audio import is_directory
from .input_file_item import InputFileItem
from .input_directory_item import InputDirectoryItem
from logging import getLogger

class InputFrame(ttk.Labelframe):

	def __init__(self, master=None, **kwargs):
		logger = getLogger(__name__)

		super().__init__(master, text='Input', **kwargs)
		logger.debug('created input frame')

		self.directory_items = list()
		self.file_items = list()
		logger.debug('setup input frame variables')

		self.header_frame = ttk.Frame(self)
		self.add_files_button = ttk.Button(self.header_frame, command=self.add_files, text='Add Files')
		self.add_directories_button = ttk.Button(self.header_frame, command=self.add_directory, text='Scan Directory')
		self.content_frame = ttk.Frame(self)
		logger.debug('created input frame children')

		self.header_frame.grid(row=0, column=0, sticky='EW')
		self.content_frame.grid(row=1, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.add_files_button.grid(row=0, column=0, sticky='EW')
		self.add_directories_button.grid(row=0, column=1, sticky='EW')
		self.header_frame.columnconfigure([0,1], weight=1)

		self.content_frame.columnconfigure(0, weight=1)
		logger.debug('layed out input frame')

	def add_files(self, *filenames):
		logger = getLogger(__name__)
		if len(filenames) < 1:
			logger.info('opening input files dialog')
			filenames = filedialog.askopenfilenames(title='Input Audio Files')
			if filenames == '':
				logger.info('no input files selected')
				return
		for filename in filenames:
			if not is_audio(filename):
				logger.warning(f'non audio input file skipped: {filename}')
				continue
			item = InputFileItem(filename, self.content_frame, self.remove_file)
			self.file_items.append(item)
			logger.info(f'audio input file listed: {filename}')
		self.__layout_items()


	def remove_file(self, item:InputFileItem):
		logger = getLogger(__name__)
		self.file_items.remove(item)
		logger.info(f'input file removed: {item.path}')
		self.__layout_items()

	def add_directory(self, directory:PathLike=None):
		logger = getLogger(__name__)
		if directory == None:
			logger.info('opening scan directory dialog')
			directory = filedialog.askdirectory(title='Input Directory to Scan', mustexist=True)
			if directory == '':
				logger.info('no input directory selected')
				return
		if not is_directory(directory):
			logger.warning(f'non-directory given as input directory: {directory}')
			return
		item = InputDirectoryItem(directory, self.remove_directory, self.add_files, self.add_directory, self.content_frame)
		self.directory_items.append(item)
		logger.info(f'input directory added: {directory}')
		self.__layout_items()

	def remove_directory(self, item:InputDirectoryItem):
		logger = getLogger(__name__)
		self.directory_items.remove(item)
		logger.info(f'input directory removed: {item.path}')
		self.__layout_items()
		
	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.directory_items:
			item.grid(column=0, row=row, sticky='EW')
			row += 1
		for item in self.file_items:
			item.grid(column=0, row=row, sticky='EW')
			row += 1
		logger.info(f'layed out {row} input items')
