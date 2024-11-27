from logging import getLogger
from os import PathLike, fspath, scandir
from queue import Queue
from typing import Generator, Self
from os.path import isdir, isfile
from ffprobe import FFProbe

class AudioScanner():

	def __init__(self, input_directories:Queue[PathLike]=None):
		logger = getLogger(__name__)
		self.output_audio: Queue[PathLike] = Queue()
		self.output_skipped: Queue[PathLike] = Queue()
		self.output_subdirectories: Queue[PathLike] = Queue()
		self.__scanner: Generator[PathLike]|None = None
		self.__current_directory: PathLike|None = None
		self.__current_path: PathLike|None = None
		if isinstance(input_directories, Queue):
			self.input_directories = input_directories
			logger.debug(f'inherited input directories queue: {input_directories}')
		else:
			self.input_directories: Queue[PathLike] = Queue()
			if input_directories is not None:
				for directory in input_directories:
					self.input_directories.put(directory)
				logger.debug(f'filled input directories queue: {input_directories}')

	def should_skip(self, path:PathLike)->bool:
		return False

	def is_directory(self, path:PathLike)->bool:
		return isdir(path)

	def is_audio(self, path:PathLike)->bool:	
		logger = getLogger(__name__)
		if not isfile(path):
			return False
		logger.debug(f'probing file: {fspath(path)}')
		try:
			probe = FFProbe(path)
		except Exception as x:
			raise RuntimeError(f"Failed to probe file: {fspath(path)}", x)
		return len(probe.audio) > 0

	def continue_scan(self):
		logger = getLogger(__name__)

		if self.__scanner is None:
			if self.input_directories.empty():
				raise StopIteration()
			directory = self.input_directories.get()
			if self.should_skip(directory):
				logger.debug(f'skipped scanning directory: {fspath(directory)}')
				self.__current_path = None
				self.output_skipped.put(directory)
				return
			logger.info(f'started scanning directory: {fspath(directory)}')
			self.__current_path = None
			self.__current_directory = directory
			self.__scanner = scandir(directory)
			return

		if self.__current_path is None:
			try:
				self.__current_path = next(self.__scanner)
			except StopIteration:
				logger.info(f'finished scanning directory: {fspath(self.__current_directory)}')
				self.close_current_directory()
				return
		
		if not self.should_skip(self.__current_path):
			if self.is_directory(self.__current_path):
				logger.debug(f'found directory: {fspath(self.__current_path)}')
				self.output_subdirectories.put(self.__current_path)
				self.__current_path = None
				return
			
			try:
				if self.is_audio(self.__current_path):
					logger.debug(f'found audio: {fspath(self.__current_path)}')
					self.output_audio.put(self.__current_path)
					self.__current_path = None
					return
			except RuntimeError as x:
				logger.error(f'failed to identify audio: {fspath(self.__current_path)}', exc_info=x)
		
		logger.debug(f'skipped scanned path: {fspath(self.__current_path)}')
		self.on_skip(self.__current_directory, self.__current_path)

	def close_current_directory(self):
		logger = getLogger(__name__)
		if self.__scanner is not None:
			self.__scanner.close()
			self.__scanner = None
			logger.info(f'closed directory: {fspath(self.__current_directory)}')
			self.__current_directory = None
			self.__current_path = None
			self.input_directories.task_done()
			logger.debug(f'{self.input_directories.unfinished_tasks} unfinished directories')

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