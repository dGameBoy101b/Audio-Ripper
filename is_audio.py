from os.path import isfile, abspath
from logging import getLogger
from os import PathLike, fspath
from ffprobe3 import probe as ffprobe

def is_audio(path:PathLike)->bool:
	logger = getLogger(__name__)
	if not isfile(path):
		return False
	logger.debug(f'probing file: {fspath(path)}')
	try:
		probe = ffprobe(abspath(path))
	except Exception as x:
		raise RuntimeError(f"Failed to probe file: {fspath(path)}", x)
	return len(probe.audio) > 0