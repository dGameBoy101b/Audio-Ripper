from logging import getLogger
from os import PathLike, fspath
from os.path import isdir, abspath, dirname
from queue import Empty
from tkinter import Event, Misc
from tkinter.ttk import Button, LabelFrame
from tkinter.filedialog import askdirectory

from mutable_queue import remove, clear
from ..audio_scanner import AudioScanner

from .input_files_frame import InputFilesFrame
from .input_directory_item import InputDirectoryItem
from .recurring_tkinter_task import ReccuringTkinterTask
from .widget_exploration import explore_descendants
from .vertical_box import VerticalBox

StrPath = PathLike|str

class DirectoryScansFrame(LabelFrame):
	def __init__(self, file_list:InputFilesFrame, scanner: AudioScanner|None = None, master:Misc|None=None, **kwargs):
		super().__init__(master, **kwargs, text='Directory Scans')
		self.file_list = file_list
		self.directories:list[StrPath] = list()
		self.scan_task = ReccuringTkinterTask(self, 'idle', self.__continue_scan)
		self.scanner = AudioScanner() if scanner is None else scanner
		self.scanner.should_skip = self.__should_skip
		self.__destroy_bindings = dict()
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.scan_directory_button = Button(self, command=self.add_directory, text='Scan Directory')
		self.clear_directories_button = Button(self, command=self.remove_all_directories, text='Clear Directories')
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.scan_directory_button.grid(row=0, column=0, sticky='EW')
		self.clear_directories_button.grid(row=0, column=1, sticky='EW')
		self.content_box.grid(row=1, column=0, columnspan=2, sticky='NSEW')
		self.content_box.content.columnconfigure(0, weight=1)
		self.columnconfigure([0,1], weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')
		
	def __directory_item_destroyed(self, event: Event):
		logger = getLogger(__name__)
		logger.debug(f'directory item destroyed: {event.widget}')
		if isinstance(event.widget, InputDirectoryItem):
			self.remove_directory(event.widget)

	def add_directory(self, directory:StrPath|None=None)->bool:
		logger = getLogger(__name__)

		if directory == None:
			logger.info('opening scan directory dialog')
			directory = askdirectory(title='Input Directory to Scan', mustexist=True)
			if directory == '':
				logger.info('no input directory selected')
				return False
		
		if abspath(directory) in self.directories:
			logger.warning(f'duplicate input directory given: {fspath(directory)}')
			return False
			
		if not isdir(directory):
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
		self.directories.append(abspath(directory))
		self.scanner.input_directories.put(directory)
		self.scan_task.schedule()
		logger.info(f'input directory added: {fspath(directory)}')
		self.__layout_items()
		return True
	
	def get_directory(self, path:StrPath)->InputDirectoryItem:
		for widget in self.content_box.content.winfo_children():
			if widget.winfo_exists() and isinstance(widget, InputDirectoryItem) and widget.get() == path:
				return widget
		raise KeyError(f"No input directory item found for path: {path}")

	def remove_directory(self, item:InputDirectoryItem|StrPath):
		logger = getLogger(__name__)
		if isinstance(item, InputDirectoryItem):
			path = item.get()
		else:
			path = item
			item = self.get_directory(path)
		path = abspath(path)
		self.directories.remove(path)
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		if self.scanner.current_directory == path:
			self.scanner.close_current_directory()
			logger.debug(f'input directory closed: {path}')
		else:
			try:
				remove(self.scanner.input_directories, path)
				logger.debug(f'input directory removed from queue: {path}')
			except ValueError:
				logger.warning(f'removed input directory not in scanner: {path}')
		logger.info(f'input directory removed: {path}')
		if len(self.directories) < 1:
			self.scan_task.unschedule()
		self.__layout_items()

	def remove_all_directories(self):
		logger = getLogger(__name__)
		to_destroy = list(self.content_box.content.winfo_children())
		self.scan_task.unschedule()
		self.scanner.close_current_directory()
		clear(self.scanner.input_directories)
		self.directories.clear()
		for item in to_destroy:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
			del self.__destroy_bindings[item]
			item.destroy()
		logger.info(f'cleared all {len(to_destroy)} directories')
		self.__layout_items()

	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.content_box.content.winfo_children():
			if not item.winfo_exists():
				continue
			item.grid(column=0, row=row, sticky='EW')
			row += 1
		logger.info(f'layed out {row} input scan items')
		self.update()

	def __should_skip(self, path:PathLike)->bool:
		return path is None or abspath(path) in self.directories or abspath(path) in self.file_list.get()

	def __increment_progress(self, directory:PathLike):
		logger = getLogger(__name__)
		for item in self.content_box.content.winfo_children():
			if isinstance(item, InputDirectoryItem) and abspath(item.get()) == abspath(directory):
				item.increment_progress()
				return
		logger.warning(f'attempted to increment progress of missing directory: {fspath(directory)}')

	def __check_audio(self)->bool:
		logger = getLogger(__name__)
		try:
			audio = self.scanner.output_audio.get(False)
		except Empty:
			return False
		logger.debug(f'got audio: {fspath(audio)}')
		self.file_list.add_file(audio)
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
		logger.debug('continuing scan...')
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

	def destroy(self):
		self.scan_task.unschedule()
		self.scanner.close_current_directory()
		clear(self.scanner.input_directories)
		for item in self.content_box.content.winfo_children():
			if item in self.__destroy_bindings:
				item.unbind('<Destroy>', self.__destroy_bindings[item])
		self.__destroy_bindings.clear()
		self.directories.clear()
		return super().destroy()