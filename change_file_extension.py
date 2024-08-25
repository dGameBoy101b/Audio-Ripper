import os.path
from pathlib import PurePath

def change_file_extension(path:PurePath, ext:str|None)->PurePath:
	path = PurePath(path)
	if ext is None:
		return path
	return path.with_suffix(str(ext))

if __name__ =='__main__':
	from scan_for_audio import scan_for_audio
	TEST_DIR = './test_dir'
	for entry in scan_for_audio(TEST_DIR):
		none = change_file_extension(entry.path, None)
		print(f'{entry.path} --> {none}')
		mp3 = change_file_extension(entry.path, '.mp3')
		print(f'{entry.path} -mp3-> {mp3}')
		