from os import PathLike
from copy_media import copy_media
from job_executor import Job

class AudioCopyJob(Job):
	def __init__(self, output_path:PathLike, input_path:PathLike,output_args:dict[str,any]):
		super().__init__(copy_media, (output_path, input_path), output_args)
