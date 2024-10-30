import os
import os.path
import logging
from collections.abc import Iterator
from ffprobe import FFProbe

def is_file(path:os.PathLike)->bool:
	return os.path.isfile(path)

def is_audio(path:os.PathLike)->bool:
	logger = logging.getLogger(__name__)
	if is_file(path):
		return False
	logger.debug(f'probing file: {path}')
	try:
		probe = FFProbe(path)
	except Exception as x:
		raise RuntimeError(f"Failed to probe file: {path}", x)
	return len(probe.audio) > 0
	
def is_directory(path:os.PathLike)->bool:
	return os.path.isdir(path)

def scan_for_audio(*root_paths:list[os.PathLike])->Iterator[os.PathLike]:
	logger = logging.getLogger(__name__)
	to_explore=list(root_paths)
	for directory in to_explore:
		logger.info(f'scanning directory for audio files: {directory}')
		with os.scandir(directory) as scan:
			for entry in scan:
				try:
					if is_audio(entry):
						logger.info(f'found audio file: {entry.path}')
						yield entry
					elif is_directory(entry):
						logger.info(f'found directory: {entry.path}')
						to_explore.append(entry.path)
					else:
						logger.info(f'skipped entry: {entry.path}')
				except Exception as x:
					logger.error(f'Failed to identify directory entry: {entry.path}', exc_info=x)

if __name__ == '__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	TEST_DIR = './test_dir'
	print(f'scanning test directory: {TEST_DIR}')
	entries = scan_for_audio(TEST_DIR)
	print('return:\n'+'\n'.join([path.path for path in entries]))