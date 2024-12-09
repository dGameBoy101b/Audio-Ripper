from os import PathLike, fspath
from os.path import dirname, isdir, abspath
from queue import Empty
from tkinter.ttk import Labelframe, Button, Scrollbar, Frame
from tkinter import Event, filedialog, Canvas
from ..audio_scanner import AudioScanner
from .input_file_item import InputFileItem
from .input_directory_item import InputDirectoryItem
from logging import getLogger

class InputFrame(Labelframe):

	def __init__(self, master=None, **kwargs):
		logger = getLogger(__name__)

		super().__init__(master, text='Input', **kwargs)
		logger.debug('created input frame')

		self.directory_items:list[InputDirectoryItem] = list()
		self.file_items:list[InputFileItem] = list()
		self.paths:set[str] = set()
		self.__scan_task_id:str|None = None
		self.scanner = AudioScanner(should_skip=self.should_skip)
		logger.debug('setup input frame variables')

		self.header_frame = Frame(self)
		self.add_files_button = Button(self.header_frame, command=self.add_files, text='Add Files')
		self.add_directories_button = Button(self.header_frame, command=self.add_directory, text='Scan Directory')
		self.clear_files_button = Button(self.header_frame, command=self.remove_all_files, text='Clear Files')
		self.clear_directories_button = Button(self.header_frame, command=self.remove_all_directories, text='Clear Directories')

		self.content_frame = Frame(self)
		self.content_canvas = Canvas(self.content_frame)
		self.content_scrollbar = Scrollbar(self.content_frame, orient='vertical', command=self.content_canvas.yview)
		self.content_canvas.config(yscrollcommand=self.content_scrollbar.set)
		self.content_canvas.bind('<Configure>', self.__resize_content)
		self.content = Frame(self.content_canvas)
		self.content.bind('<Configure>', self.__update_scrollregion)
		self.content_id = self.content_canvas.create_window(0, 0, anchor='nw', window=self.content)

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

		self.content_canvas.grid(row=0, column=0, sticky='NSEW')
		self.content_canvas.columnconfigure(0, weight=1)
		self.content_scrollbar.grid(row=0, column=1, sticky='NSE')
		self.content_frame.columnconfigure(0, weight=1)
		self.content_frame.rowconfigure(0, weight=1)

		self.content.columnconfigure(0, weight=1)
		self.content.rowconfigure(0, weight=1)
		logger.debug('layed out input frame')

	def __resize_content(self, event: Event):
		self.content_canvas.itemconfig(self.content_id, width=event.width)

	def __update_scrollregion(self, event:Event=None):
		self.content_canvas.config(scrollregion=self.content_canvas.bbox(self.content_id))

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
			if self.should_skip(filename):
				logger.warning(f'duplicate input file skipped: {fspath(filename)}')
				continue
			if not self.scanner.is_audio(filename):
				logger.warning(f'non audio input file skipped: {fspath(filename)}')
				continue
			item = InputFileItem(filename, self.content, on_remove=self.remove_file)
			self.file_items.append(item)
			self.paths.add(abspath(filename))
			logger.info(f'audio input file listed: {fspath(filename)}')

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
		logger.debug('got nothing')

	def __continue_scan(self):
		logger = getLogger(__name__)
		self.__scan_task_id = None
		try:
			self.scanner.continue_scan()
			logger.debug('continued input directory scan')
			self.__check_progress()
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
		
		if self.should_skip(directory):
			logger.warning(f'duplicate input directory given: {fspath(directory)}')
			return False
			
		if not self.scanner.is_directory(directory):
			logger.warning(f'non-directory given as input directory: {fspath(directory)}')
			return False
		
		try:
			item = InputDirectoryItem(directory, self.content, on_remove=self.remove_directory)
		except OSError as x:
			logger.error(f'failed to add input directory: {fspath(directory)}', exc_info=x)
			return False

		self.directory_items.append(item)
		self.paths.add(abspath(directory))
		if enqueue:
			self.scanner.input_directories.put(directory)
		logger.info(f'input directory added: {fspath(directory)}')
		self.schedule_scan()
		self.__layout_items()
		return True

	def remove_directory(self, item:InputDirectoryItem):
		logger = getLogger(__name__)
		self.directory_items.remove(item)
		self.paths.remove(abspath(item.path))
		logger.info(f'input directory removed: {fspath(item.path)}')
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
		self.__update_scrollregion()
		self.update()

	def destroy(self):
		self.cancel_scan()
		return super().destroy()
