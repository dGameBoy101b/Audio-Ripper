from collections.abc import Iterator
from os import PathLike, scandir
from os.path import isdir

from .is_audio import is_audio

def scan_for_audio(*root_paths:PathLike)->Iterator[PathLike]:
	to_explore = list(reversed(root_paths))
	while len(to_explore) > 0:
		root = to_explore.pop()
		for path in scandir(root):
			if isdir(path):
				to_explore.append(path)
			elif is_audio(path):
				yield path

if __name__ == '__main__':
	import logging
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	TEST_DIR = './test_dir'
	print(f'scanning test directory: {TEST_DIR}')
	entries = scan_for_audio(TEST_DIR)
	print('return:\n'+'\n'.join([path.path for path in entries]))