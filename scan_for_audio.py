import os
import logging
from collections.abc import Iterator
from ffprobe import FFProbe

def scan_for_audio(*root_paths:list[str])->Iterator[os.DirEntry]:
	logger = logging.getLogger(__name__)

	def is_audio(entry:os.DirEntry)->bool:
		if not entry.is_file():
			return False
		logger.debug(f'probing file: {entry.path}')
		try:
			probe = FFProbe(entry.path)
		except Exception as x:
			raise RuntimeError(f"Failed to probe file: {entry.path}", x)
		return len(probe.audio) > 0
	
	def is_directory(entry:os.DirEntry)->bool:
		return entry.is_dir()
	
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