from os import PathLike
from pathlib import PurePath

StrPath = PathLike|str

def change_file_extension(path:StrPath, ext:str|None)->PathLike:
	path = PurePath(path)
	if ext is None:
		return path
	return path.with_suffix(str(ext))

if __name__ =='__main__':
	from scan_for_audio import scan_for_audio
	from os import fspath
	TEST_DIR = './test_dir'
	for entry in scan_for_audio(TEST_DIR):
		none = change_file_extension(entry, None)
		print(f'{fspath(entry)} --> {none}')
		mp3 = change_file_extension(entry, '.mp3')
		print(f'{fspath(entry)} -mp3-> {mp3}')
		