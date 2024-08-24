import ffmpeg
import logging
from collections.abc import Callable

def copy_media(output_filepath:str, input_filepath:str, transform:Callable[['stream'], 'stream']=lambda x: x):
	logger = logging.getLogger(__name__)
	logger.info(f'copying {input_filepath} to {output_filepath}')
	logger.debug(f'creating input stream: {input_filepath}')
	input_stream = ffmpeg.input(input_filepath)
	logger.debug(f'transforming data: {transform}')
	transform_stream = transform(input_stream)
	logger.debug(f'creating output stream: {output_filepath}')
	output_stream = ffmpeg.output(transform_stream, output_filepath)
	logger.debug('creating overwrite stream')
	overwrite_stream = ffmpeg.overwrite_output(output_stream)
	logger.debug('running ffmpeg...')
	ffmpeg.run(overwrite_stream)
	logger.info(f'copied {input_filepath} to {output_filepath}')

if __name__ == '__main__':
	from scan_for_audio import scan_for_audio
	import os.path
	import sys
	IN_DIR='./test_dir'
	OUT_DIR='./test_out'
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	print(f'copying audio from {IN_DIR} to {OUT_DIR}')
	for audio_file in scan_for_audio(IN_DIR):
		input_path = audio_file.path
		output_path = os.path.join(OUT_DIR, audio_file.name)
		print(f'copying {input_path} to {output_path}')
		copy_media(output_path, input_path)
		print(f'successfully copied {input_path} to {output_path}')