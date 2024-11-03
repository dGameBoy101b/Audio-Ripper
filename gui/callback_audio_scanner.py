from os import PathLike
from queue import Queue
from typing import Callable
from ..audio_scanner import AudioScanner

class CallbackAudioScanner(AudioScanner):

	def __init__(self, input_directories:Queue[PathLike]=None, *, 
			  on_start_directory:Callable[[PathLike],None]=None, on_finish_directory:Callable[[PathLike],None]=None,
			  is_directory:Callable[[PathLike],bool]=None, on_subdirectory:Callable[[PathLike,PathLike],None]=None, 
			  is_audio:Callable[[PathLike],bool]=None, on_audio:Callable[[PathLike,PathLike],None]=None,
			  should_skip:Callable[[PathLike],bool]=None, on_skip:Callable[[PathLike,PathLike|None],None]=None):
		super().__init__(input_directories)
		self.start_directory_callabck = on_start_directory
		self.finish_directory_callback = on_finish_directory
		self.directory_predicate = is_directory
		self.subdirectory_callback = on_subdirectory
		self.audio_predicate = is_audio
		self.audio_callback = on_audio
		self.skip_predicate = should_skip
		self.skip_callback = on_skip

	def on_start_directory(self, directory:PathLike):
		super().on_start_directory(directory)
		if self.start_directory_callabck is not None:
			self.start_directory_callabck(directory)

	def on_finish_directory(self, directory:PathLike):
		super().on_finish_directory(directory)
		if self.finish_directory_callback is not None:
			self.finish_directory_callback(directory)

	def is_directory(self, path:PathLike)->bool:
		if self.directory_predicate is not None:
			return self.directory_predicate(path)
		return super().is_directory(path)
	
	def on_subdirectory(self, directory:PathLike, sub_directory:PathLike):
		super().on_subdirectory(directory, sub_directory)
		if self.subdirectory_callback is not None:
			self.subdirectory_callback(directory, sub_directory)

	def is_audio(self, path:PathLike):
		if self.audio_predicate is not None:
			return self.audio_predicate(path)
		return super().is_audio(path)

	def on_audio(self, directory:PathLike, audio:PathLike):
		super().on_audio(directory, audio)
		if self.audio_callback is not None:
			self.audio_callback(directory, audio)

	def should_skip(self, path:PathLike):
		if self.skip_predicate is not None:
			return self.skip_predicate(path)
		return super().should_skip(path)
	
	def on_skip(self, directory:PathLike, path:PathLike|None):
		super().on_skip(directory, path)
		if self.skip_callback is not None:
			self.skip_callback(directory, path)
