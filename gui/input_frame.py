from os import PathLike
from tkinter import ttk
from tkinter import filedialog
from .input_file_item import InputFileItem
from .input_directory_item import InputDirectoryItem
from logging import getLogger
from os.path import abspath
from .callback_audio_scanner import CallbackAudioScanner

class InputFrame(ttk.Labelframe):

	def __init__(self, master=None, **kwargs):
		logger = getLogger(__name__)

		super().__init__(master, text='Input', **kwargs)
		logger.debug('created input frame')

		self.directory_items:list[InputDirectoryItem] = list()
		self.file_items:list[InputFileItem] = list()
		self.paths:set[str] = set()
		self.__scan_task_id:str|None = None
		self.scanner = CallbackAudioScanner(on_subdirectory=self.__on_subdirectory, on_audio=self.__on_audio, on_skip=self.__on_skip)
		logger.debug('setup input frame variables')

		self.header_frame = ttk.Frame(self)
		self.add_files_button = ttk.Button(self.header_frame, command=self.add_files, text='Add Files')
		self.add_directories_button = ttk.Button(self.header_frame, command=self.add_directory, text='Scan Directory')
		self.clear_files_button = ttk.Button(self.header_frame, command=self.remove_all_files, text='Clear Files')
		self.clear_directories_button = ttk.Button(self.header_frame, command=self.remove_all_directories, text='Clear Directories')
		self.content_frame = ttk.Frame(self)
		logger.debug('created input frame children')

		self.header_frame.grid(row=0, column=0, sticky='EW')
		self.content_frame.grid(row=1, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.add_files_button.grid(row=0, column=0, sticky='EW')
		self.add_directories_button.grid(row=0, column=1, sticky='EW')
		self.clear_files_button.grid(row=1, column=0, sticky='EW')
		self.clear_directories_button.grid(row=1, column=1, sticky='EW')
		self.header_frame.columnconfigure([0,1], weight=1)

		self.content_frame.columnconfigure(0, weight=1)
		logger.debug('layed out input frame')

	def __on_subdirectory(self, directory:PathLike, subdirectory:PathLike):
		self.__increment_progress(directory)
		self.add_directory(subdirectory, False)

	def __on_audio(self, directory:PathLike, audio:PathLike):
		self.__increment_progress(directory)
		self.scanner.output_audio.task_done()
		self.add_files(audio)

	def __on_skip(self, directory:PathLike, path:PathLike|None):
		if path is None:
			self.remove_directory(directory)
		else:
			self.__increment_progress(directory)

	def __increment_progress(self, directory:PathLike):
		logger = getLogger(__name__)
		for item in self.directory_items:
			if abspath(item.path) == abspath(directory):
				item.increment_progress()
				return
		logger.warning(f'attempted to increment progress of missing directory: {directory}')

	def add_files(self, *filenames):
		logger = getLogger(__name__)

		if len(filenames) < 1:
			logger.info('opening input files dialog')
			filenames = filedialog.askopenfilenames(title='Input Audio Files')
			if filenames == '':
				logger.info('no input files selected')
				return
			
		for filename in filenames:
			if not self.should_scan(filename):
				logger.warning(f'duplicate input file skipped: {abspath(filename)}')
				continue
			if not self.scanner.is_audio(filename):
				logger.warning(f'non audio input file skipped: {abspath(filename)}')
				continue
			item = InputFileItem(filename, self.content_frame, on_remove=self.remove_file)
			self.file_items.append(item)
			self.paths.add(abspath(filename))
			logger.info(f'audio input file listed: {abspath(filename)}')

		self.__layout_items()

	def remove_file(self, item:InputFileItem):
		logger = getLogger(__name__)
		self.file_items.remove(item)
		self.paths.remove(abspath(item.path))
		logger.info(f'input file removed: {abspath(item.path)}')
		self.__layout_items()

	def remove_all_files(self):
		logger = getLogger(__name__)
		paths = set()
		for item in self.file_items:
			item.destroy()
			paths.add(abspath(item.path))
		self.file_items.clear()
		self.paths -= paths
		logger.info(f'cleared all {len(paths)} files')
		self.__layout_items()

	def should_scan(self, path:PathLike):
		return path is not None and abspath(path) not in self.paths

	def __continue_scan(self):
		logger = getLogger(__name__)
		self.__scan_task_id = None
		try:
			self.scanner.continue_scan()
			logger.debug('continued input directory scan')
		except StopIteration:
			logger.warning('attempted to continue scan while input directory queue empty')
			return
		self.schedule_scan()

	def schedule_scan(self, milliseconds:int=0)->bool:
		logger = getLogger(__name__)
		if len(self.directory_items) < 1:
			return False
		if self.is_scan_scheduled():
			return True
		self.__scan_task_id = self.after(milliseconds, self.__continue_scan)
		logger.debug(f'scheduled directory scan in {milliseconds} milliseconds')
		return True
	
	def is_scan_scheduled(self)->bool:
		return self.__scan_task_id is not None
	
	def cancel_scan(self):
		if self.is_scan_scheduled():
			self.after_cancel(self.__scan_task_id)
			self.__scan_task_id = None

	def add_directory(self, directory:PathLike=None, enqueue:bool=True)->bool:
		logger = getLogger(__name__)

		if directory == None:
			logger.info('opening scan directory dialog')
			directory = filedialog.askdirectory(title='Input Directory to Scan', mustexist=True)
			if directory == '':
				logger.info('no input directory selected')
				return False
		
		if not self.should_scan(directory):
			logger.warning(f'duplicate input directory given: {abspath(directory)}')
			return False
			
		if not self.scanner.is_directory(directory):
			logger.warning(f'non-directory given as input directory: {abspath(directory)}')
			return False
		
		try:
			item = InputDirectoryItem(directory, self.content_frame, on_remove=self.remove_directory)
		except OSError as x:
			logger.error(f'failed to add input directory: {abspath(directory)}', exc_info=x)
			return False

		self.directory_items.append(item)
		self.paths.add(abspath(directory))
		if enqueue:
			self.scanner.input_directories.put(directory)
		logger.info(f'input directory added: {abspath(directory)}')
		self.schedule_scan()
		self.__layout_items()
		return True

	def remove_directory(self, item:InputDirectoryItem):
		logger = getLogger(__name__)
		self.directory_items.remove(item)
		self.paths.remove(abspath(item.path))
		logger.info(f'input directory removed: {abspath(item.path)}')
		self.schedule_scan()
		self.__layout_items()

	def remove_all_directories(self):
		logger = getLogger(__name__)
		paths = set()
		self.cancel_scan()
		for item in self.directory_items:
			item.destroy()
			paths.add(abspath(item.path))
		self.directory_items.clear()
		self.paths -= paths
		logger.info(f'cleared all {len(paths)} directories')
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
		self.update()

	def destroy(self):
		self.cancel_scan()
		return super().destroy()
