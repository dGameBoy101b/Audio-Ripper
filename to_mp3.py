import os.path

def change_file_extension(path:str, ext:str)->str:
	return os.path.splitext(path)[0]+ext

def to_mp3(path:str)->str:
	return change_file_extension(path, '.mp3')

if __name__ =='__main__':
	from scan_for_audio import scan_for_audio
	TEST_DIR = './test_dir'
	for entry in scan_for_audio(TEST_DIR):
		mp3 = to_mp3(entry.path)
		print(f'{entry.path} -mp3-> {mp3}')
		