from os import PathLike
from pathlib import Path, PurePath
import ffmpeg
import logging

StrPath = PathLike|str

def copy_media(output_filepath:StrPath, input_filepath:StrPath, **kwargs):
	logger = logging.getLogger(__name__)
	output_filepath = PurePath(output_filepath)
	input_filepath = PurePath(input_filepath)
	if output_filepath == input_filepath:
		logger.debug(f'skipped copying to same path: {input_filepath}')
		return
	logger.info(f'copying {input_filepath} to {output_filepath}')
	Path(output_filepath.parent).mkdir(parents=True, exist_ok=True)
	logger.debug(f'creating input stream: {input_filepath}')
	input_stream = ffmpeg.input(input_filepath)
	logger.debug(f'creating output stream: {output_filepath}')
	output_stream = ffmpeg.output(input_stream, str(output_filepath), **kwargs)
	logger.debug('creating overwrite stream')
	overwrite_stream = ffmpeg.overwrite_output(output_stream)
	logger.debug('running ffmpeg...')
	(_, out) = ffmpeg.run(overwrite_stream, capture_stderr=True) #it's actually stderr that ffmpeg uses for reporting
	if out:
		logger.debug(out.decode())
	logger.info(f'copied {input_filepath} to {output_filepath}')

if __name__ == '__main__':
	from scan_for_audio import scan_for_audio
	from os.path import basename, join
	from os import fspath
	from sys import stdout
	IN_DIR='./test_dir'
	OUT_DIR='./test_out'
	logging.basicConfig(level=logging.DEBUG, stream=stdout)
	print(f'copying audio from {IN_DIR} to {OUT_DIR}')
	for audio_file in scan_for_audio(IN_DIR):
		input_path = fspath(audio_file)
		output_path = join(OUT_DIR, basename(audio_file))
		print(f'copying {input_path} to {output_path}')
		copy_media(output_path, input_path)
		print(f'successfully copied {input_path} to {output_path}')