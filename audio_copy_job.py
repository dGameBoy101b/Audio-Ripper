from os import PathLike
from typing import Any
from .copy_media import copy_media
from .job_executor import Job

class AudioCopyJob(Job):
	def __init__(self, output_path:PathLike, input_path:PathLike,output_args:dict[str,Any]):
		super().__init__(copy_media, (output_path, input_path), output_args)

	def __getattr__(self, name:str)->Any:
		if name == 'output_path':
			return self.args[0]
		if name == 'input_path':
			return self.args[1]
		if name == 'output_args':
			return self.kwargs
		raise AttributeError(name=name, obj=self)
