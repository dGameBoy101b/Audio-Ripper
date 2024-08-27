from pathlib import Path
import ffmpeg
import logging

def copy_media(output_filepath:Path, input_filepath:Path, **kwargs):
	logger = logging.getLogger(__name__)
	output_filepath = Path(output_filepath)
	input_filepath = Path(input_filepath)
	logger.info(f'copying {input_filepath} to {output_filepath}')
	output_filepath.mkdir(parents=True, exist_ok=True)
	logger.debug(f'creating input stream: {input_filepath}')
	input_stream = ffmpeg.input(input_filepath)
	logger.debug(f'creating output stream: {output_filepath}')
	output_stream = ffmpeg.output(input_stream, output_filepath, **kwargs)
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