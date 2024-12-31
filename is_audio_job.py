from os import PathLike
from typing import Any
from job_executor import Job

from .is_audio import is_audio

class IsAudioJob(Job):
	def __init__(self, path:PathLike):
		super().__init__(is_audio, (path,))

	def __getattr__(self, name:str)->Any:
		if name == 'path':
			return self.args[0]