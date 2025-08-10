from logging import getLogger
from os import PathLike, fspath, scandir
from queue import Empty, Queue
from typing import Callable, Iterable, Self
from os.path import isdir

from .is_audio import is_audio

StrPath = PathLike|str

class AudioScanner():

	def __init__(self, input_directories:Queue[StrPath]|Iterable[StrPath]|None=None, should_skip:Callable[[PathLike],bool]|None=None):
		logger = getLogger(__name__)
		self.output_audio: Queue[PathLike] = Queue()
		self.output_skipped: Queue[PathLike] = Queue()
		self.output_subdirectories: Queue[PathLike] = Queue()
		self.__scanner = None
		self.__current_directory = None
		self.__current_path = None
		if isinstance(input_directories, Queue):
			self.input_directories = input_directories
			logger.debug(f'inherited input directories queue: {input_directories}')
		else:
			self.input_directories: Queue[StrPath] = Queue()
			if input_directories is not None:
				for directory in input_directories:
					self.input_directories.put(directory)
				logger.debug(f'filled input directories queue: {input_directories}')
		self.should_skip = (lambda path: False) if should_skip is None else should_skip

	def try_output_skip(self, path:PathLike)->bool:
		if not self.should_skip(path):
			return False
		self.output_skip(path)
		return True
	
	def output_skip(self, path:PathLike):
		logger = getLogger(__name__)
		logger.debug(f'skipped scanned path: {fspath(path)}')
		self.output_skipped.put(path)
	
	def try_output_directory(self, path:PathLike)->bool:
		if not isdir(path):
			return False
		self.output_directory(path)
		return True
	
	def output_directory(self, directory:PathLike):
		logger = getLogger(__name__)
		logger.debug(f'found directory: {fspath(directory)}')
		self.output_subdirectories.put(directory)
	
	def try_output_audio_file(self, path:PathLike)->bool:
		logger = getLogger(__name__)
		try:
			result = is_audio(path)
		except RuntimeError as x:
			logger.error(f'failed to identify audio: {fspath(path)}', exc_info=x)
			return False
		if not result:
			return False
		self.output_audio_file(path)
		return True
		
	def output_audio_file(self, audio:PathLike):
		logger = getLogger(__name__)
		logger.debug(f'found audio: {fspath(audio)}')
		self.output_audio.put(audio)

	def open_next_directory(self):
		logger = getLogger(__name__)
		if self.__scanner is not None:
			self.close_current_directory()
		try:
			directory = self.input_directories.get(False)
		except Empty:
			raise StopIteration()
		logger.info(f'started scanning directory: {fspath(directory)}')
		self.__current_path = None
		self.__current_directory = directory
		self.__scanner = scandir(directory)

	def try_get_next_path(self)->bool:
		logger = getLogger(__name__)
		if self.__current_path is not None:
			return True
		if self.__scanner is None:
			return False
		try:
			self.__current_path = next(self.__scanner)
		except StopIteration:
			logger.info(f'finished scanning directory: {fspath(self.__current_directory)}')
			self.close_current_directory()
			return False
		return True

	def continue_scan(self):
		if self.__scanner is None:
			self.open_next_directory()
			return

		if not self.try_get_next_path():
			return
		
		if self.try_output_skip(self.__current_path):
			self.__current_path = None
			return
		
		if self.try_output_directory(self.__current_path):
			self.__current_path = None
			return
		
		if self.try_output_audio_file(self.__current_path):
			self.__current_path = None
			return
		
		self.output_skip(self.__current_path)
		self.__current_path = None

	def close_current_directory(self):
		logger = getLogger(__name__)
		if self.__scanner is None:
			return
		self.__scanner.close()
		self.__scanner = None
		logger.info(f'closed directory: {fspath(self.__current_directory)}')
		self.__current_directory = None
		self.__current_path = None
		self.input_directories.task_done()
		logger.debug(f'{self.input_directories.unfinished_tasks} unfinished directories')

	def __getattr__(self, name):
		if name == 'current_directory':
			return self.__current_directory
		if name == 'current_path':
			return self.__current_path
		raise AttributeError(name=name, obj=self)

	def __del__(self):
		self.close_current_directory()

	def __enter__(self)->Self:
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close_current_directory()

	def __iter__(self)->Self:
		return self
	
	def __next__(self)->PathLike:
		while self.output_audio.empty():
			self.continue_scan()
		audio = self.output_audio.get()
		self.output_audio.task_done()
		return audio