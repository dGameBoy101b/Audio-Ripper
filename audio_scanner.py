from logging import getLogger
from os import PathLike, scandir
from queue import Queue
from typing import Self
from os.path import isdir, isfile
from ffprobe import FFProbe

class AudioScanner():

	def __init__(self, input_directories:Queue[PathLike]=None):
		logger = getLogger(__name__)
		self.output_audio = Queue()
		self.scanner = None
		self.__current_directory = None
		if isinstance(input_directories, Queue):
			self.input_directories = input_directories
			logger.debug(f'inherited input directories queue: {input_directories}')
		else:
			self.input_directories = Queue()
			if input_directories is not None:
				for directory in input_directories:
					self.input_directories.put(directory)
				logger.debug(f'filled input directories queue: {input_directories}')

	def is_directory(self, path:PathLike)->bool:
		return isdir(path)

	def is_audio(self, path:PathLike)->bool:	
		logger = getLogger(__name__)
		if not isfile(path):
			return False
		logger.debug(f'probing file: {path}')
		try:
			probe = FFProbe(path)
		except Exception as x:
			raise RuntimeError(f"Failed to probe file: {path}", x)
		return len(probe.audio) > 0
	
	def on_dirctory(self, directory:PathLike):
		self.input_directories.put(directory)

	def on_audio(self, audio:PathLike):
		self.output_audio.put(audio)

	def continue_scan(self):
		logger = getLogger(__name__)

		if self.scanner is None:
			if self.input_directories.empty():
				raise StopIteration()
			self.__current_directory = self.input_directories.get()
			self.scanner = scandir(self.__current_directory)
			logger.info(f'started scanning directory: {self.__current_directory}')

		try:
			path = next(self.scanner)
		except StopIteration:
			logger.info(f'finished scanning directory: {self.__current_directory}')
			self.close_current_directory()
			return
		
		if self.is_directory(path):
			logger.debug(f'found directory: {path}')
			self.on_dirctory(path)
			return
		
		try:
			if self.is_audio(path):
				logger.debug(f'found audio: {path}')
				self.on_audio(path)
				return
		except RuntimeError as x:
			logger.error(f'failed to identify audio: {path}', exc_info=x)
		
		logger.debug(f'skipped scanned path: {path}')

	def close_current_directory(self):
		if self.scanner is not None:
			self.scanner.close()
			self.scanner = None
			self.__current_directory = None
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