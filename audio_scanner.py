from logging import getLogger
from os import PathLike, scandir
from queue import Queue
from typing import Generator, Self
from os.path import isdir, isfile, abspath
from ffprobe import FFProbe

class AudioScanner():

	def __init__(self, input_directories:Queue[PathLike]=None):
		logger = getLogger(__name__)
		self.output_audio = Queue()
		self.__scanner: Generator[PathLike]|None = None
		self.__current_directory: PathLike|None = None
		self.__current_path: PathLike|None = None
		if isinstance(input_directories, Queue):
			self.input_directories = input_directories
			logger.debug(f'inherited input directories queue: {input_directories}')
		else:
			self.input_directories = Queue()
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
		logger.debug(f'probing file: {abspath(path)}')
		try:
			probe = FFProbe(path)
		except Exception as x:
			raise RuntimeError(f"Failed to probe file: {path}", x)
		return len(probe.audio) > 0
	
	def on_subdirectory(self, directory:PathLike, subdirectory:PathLike):
		self.input_directories.put(subdirectory)
		self.__current_path = None

	def on_audio(self, directory:PathLike, audio:PathLike):
		self.output_audio.put(audio)
		self.__current_path = None

	def on_start_directory(self, directory:PathLike):
		self.__current_path = None
		self.__current_directory = directory
		self.__scanner = scandir(directory)

	def on_skip(self, directory:PathLike, path:PathLike|None):
		self.__current_path = None

	def on_finish_directory(self, directory:PathLike):
		self.close_current_directory()

	def continue_scan(self):
		logger = getLogger(__name__)

		if self.__scanner is None:
			if self.input_directories.empty():
				raise StopIteration()
			directory = self.input_directories.get()
			if self.should_skip(directory):
				logger.debug(f'skipped scanning directory: {abspath(directory)}')
				self.on_skip(directory, None)
				return
			logger.info(f'started scanning directory: {abspath(directory)}')
			self.on_start_directory(directory)
			return

		if self.__current_path is None:
			try:
				self.__current_path = next(self.__scanner)
			except StopIteration:
				logger.info(f'finished scanning directory: {abspath(self.__current_directory)}')
				self.on_finish_directory(self.__current_directory)
				return
		
		if not self.should_skip(self.__current_path):
			if self.is_directory(self.__current_path):
				logger.debug(f'found directory: {abspath(self.__current_path)}')
				self.on_subdirectory(self.__current_directory, self.__current_path)
				return
			
			try:
				if self.is_audio(self.__current_path):
					logger.debug(f'found audio: {abspath(self.__current_path)}')
					self.on_audio(self.__current_directory, self.__current_path)
					return
			except RuntimeError as x:
				logger.error(f'failed to identify audio: {abspath(self.__current_path)}', exc_info=x)
		
		logger.debug(f'skipped scanned path: {abspath(self.__current_path)}')
		self.on_skip(self.__current_directory, self.__current_path)

	def close_current_directory(self):
		if self.__scanner is not None:
			self.__scanner.close()
			self.__scanner = None
			self.__current_directory = None
			self.__current_path = None
			self.input_directories.task_done()

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
		return audio