from collections.abc import Iterator
from .audio_scanner import AudioScanner
from os import PathLike

def scan_for_audio(*root_paths:list[PathLike])->Iterator[PathLike]:
	with AudioScanner(root_paths) as scanner:
		yield from scanner

if __name__ == '__main__':
	import logging
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	TEST_DIR = './test_dir'
	print(f'scanning test directory: {TEST_DIR}')
	entries = scan_for_audio(TEST_DIR)
	print('return:\n'+'\n'.join([path.path for path in entries]))