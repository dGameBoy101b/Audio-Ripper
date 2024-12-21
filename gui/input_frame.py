from os import PathLike, fspath
from os.path import dirname, isdir, abspath
from queue import Empty
from tkinter.ttk import Labelframe, Button, Frame
from tkinter import Event, filedialog
from logging import getLogger

from ..audio_scanner import AudioScanner

from .recurring_tkinter_task import ReccuringTkinterTask
from .widget_exploration import explore_descendants
from .vertical_box import VerticalBox
from .input_file_item import InputFileItem
from .input_directory_item import InputDirectoryItem

class InputFrame(Labelframe):

	def __init__(self, master=None, **kwargs):
		super().__init__(master, text='Input', **kwargs)

		self.directory_items:list[InputDirectoryItem] = list()
		self.file_items:list[InputFileItem] = list()
		self.paths:set[str] = set()
		self.scan_task = ReccuringTkinterTask(self, 0, self.__continue_scan)
		self.scanner = AudioScanner(should_skip=self.should_skip)
		self.__destroy_bindings = dict()

		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.header_frame = Frame(self)
		self.add_files_button = Button(self.header_frame, command=self.add_files, text='Add Files')
		self.add_directories_button = Button(self.header_frame, command=self.add_directory, text='Scan Directory')
		self.clear_files_button = Button(self.header_frame, command=self.remove_all_files, text='Clear Files')
		self.clear_directories_button = Button(self.header_frame, command=self.remove_all_directories, text='Clear Directories')
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.header_frame.grid(row=0, column=0, sticky='EW')
		self.content_box.grid(row=1, column=0, sticky='NSEW')
		self.content_box.content.columnconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.add_files_button.grid(row=0, column=0, sticky='EW')
		self.add_directories_button.grid(row=0, column=1, sticky='EW')
		self.clear_files_button.grid(row=1, column=0, sticky='EW')
		self.clear_directories_button.grid(row=1, column=1, sticky='EW')
		self.header_frame.columnconfigure([0,1], weight=1)
		logger.debug(f'grid configured: {self}')

	def __increment_progress(self, directory:PathLike):
		logger = getLogger(__name__)
		for item in self.directory_items:
			if abspath(item.get()) == abspath(directory):
				item.increment_progress()
				return
		logger.warning(f'attempted to increment progress of missing directory: {directory}')

	def __file_item_destroyed(self, event:Event):
		self.remove_file(event.widget)

	def add_files(self, *filenames):
		logger = getLogger(__name__)

		if len(filenames) < 1:
			logger.info('opening input files dialog')
			filenames = filedialog.askopenfilenames(title='Input Audio Files')
			if filenames == '':
				logger.info('no input files selected')
				return
			
		for filename in filenames:
			if self.should_skip(filename):
				logger.warning(f'duplicate input file skipped: {fspath(filename)}')
				continue
			if not self.scanner.is_audio(filename):
				logger.warning(f'non audio input file skipped: {fspath(filename)}')
				continue
			item = InputFileItem(filename, self.content_box.content)
			binding = item.bind('<Destroy>', self.__file_item_destroyed)
			self.__destroy_bindings[item] = binding
			for widget in explore_descendants(item):
				self.content_box.bind_scroll_forwarding(widget)
			self.file_items.append(item)
			self.paths.add(abspath(filename))
			logger.info(f'audio input file listed: {fspath(filename)}')
			self.__layout_items()

	def remove_file(self, item:InputFileItem):
		logger = getLogger(__name__)
		self.file_items.remove(item)
		path = item.get()
		self.paths.remove(abspath(path))
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		logger.info(f'input file removed: {abspath(path)}')
		self.__layout_items()

	def remove_all_files(self):
		logger = getLogger(__name__)
		to_destroy = list(self.file_items)
		paths = set([abspath(item.get()) for item in self.file_items])
		self.file_items.clear()
		self.paths -= paths
		for item in to_destroy:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
			del self.__destroy_bindings[item]
			item.destroy()
		logger.info(f'cleared all {len(to_destroy)} files')
		self.__layout_items()

	def should_skip(self, path:PathLike):
		return path is None or abspath(path) in self.paths
	
	def __check_audio(self)->bool:
		logger = getLogger(__name__)
		try:
			audio = self.scanner.output_audio.get(False)
		except Empty:
			return False
		logger.debug(f'got audio: {fspath(audio)}')
		self.add_files(audio)
		self.__increment_progress(dirname(audio))
		self.scanner.output_audio.task_done()
		return True
		
	def __check_subdirectories(self)->bool:
		logger = getLogger(__name__)
		try:
			subdirectory = self.scanner.output_subdirectories.get(False)
		except Empty:
			return False
		logger.debug(f'got subdirectory: {fspath(subdirectory)}')
		self.__increment_progress(dirname(subdirectory))
		self.add_directory(subdirectory)
		self.scanner.output_subdirectories.task_done()
		return True

	def __check_skipped(self)->bool:
		logger = getLogger(__name__)
		try:
			skipped = self.scanner.output_skipped.get(False)
		except Empty:
			return False
		logger.debug(f'got skipped: {fspath(skipped)}')
		if isdir(skipped):
			self.remove_directory(skipped)
		else:
			self.__increment_progress(dirname(skipped))
		self.scanner.output_skipped.task_done()
		return True

	def __check_progress(self):
		logger = getLogger(__name__)
		if self.__check_audio():
			return
		if self.__check_subdirectories():
			return
		if self.__check_skipped():
			return
		logger.debug('no progress found')

	def __continue_scan(self):
		logger = getLogger(__name__)
		try:
			self.scanner.continue_scan()
		except StopIteration:
			logger.warning('attempted to continue scan while input directory queue empty')
			self.scan_task.unschedule()
			return
		logger.debug('continued input directory scan')
		self.update()
		self.__check_progress()
		logger.debug('checked scan progress')
		self.update()

	def __directory_item_destroyed(self, event: Event):
		self.remove_directory(event.widget)

	def add_directory(self, directory:PathLike=None)->bool:
		logger = getLogger(__name__)

		if directory == None:
			logger.info('opening scan directory dialog')
			directory = filedialog.askdirectory(title='Input Directory to Scan', mustexist=True)
			if directory == '':
				logger.info('no input directory selected')
				return False
		
		if self.should_skip(directory):
			logger.warning(f'duplicate input directory given: {fspath(directory)}')
			return False
			
		if not self.scanner.is_directory(directory):
			logger.warning(f'non-directory given as input directory: {fspath(directory)}')
			return False
		
		try:
			item = InputDirectoryItem(directory, self.content_box.content)
		except OSError as x:
			logger.error(f'failed to add input directory: {fspath(directory)}', exc_info=x)
			return False

		binding = item.bind('<Destroy>', self.__directory_item_destroyed)
		self.__destroy_bindings[item] = binding
		for widget in explore_descendants(item):
			self.content_box.bind_scroll_forwarding(widget)
		self.directory_items.append(item)
		self.paths.add(abspath(directory))
		self.scanner.input_directories.put(directory)
		self.scan_task.schedule()
		logger.info(f'input directory added: {fspath(directory)}')
		self.__layout_items()
		return True

	def remove_directory(self, item:InputDirectoryItem):
		logger = getLogger(__name__)
		self.directory_items.remove(item)
		path = item.get()
		self.paths.remove(abspath(path))
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		logger.info(f'input directory removed: {fspath(path)}')
		if len(self.directory_items) < 1:
			self.scan_task.unschedule()
		self.__layout_items()

	def remove_all_directories(self):
		logger = getLogger(__name__)
		to_destroy = list(self.directory_items)
		paths = set([abspath(item.get()) for item in self.directory_items])
		self.scan_task.unschedule()
		self.directory_items.clear()
		self.paths -= paths
		for item in to_destroy:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
			del self.__destroy_bindings[item]
			item.destroy()
		logger.info(f'cleared all {len(to_destroy)} directories')
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
		self.scan_task.unschedule()
		for item in self.file_items + self.directory_items:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
		self.__destroy_bindings.clear()
		self.paths.clear()
		self.file_items.clear()
		self.directory_items.clear()
		return super().destroy()

	def get(self)->list[PathLike]:
		return [item.get() for item in self.file_items]