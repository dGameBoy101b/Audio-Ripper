from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from override_media_metadata import override_media_metadata
from change_file_extension import change_file_extension
from copy_media import copy_media
import os.path
import time
from pathlib import PurePath

def rip_sequential(output_dir:PurePath, input_dir:PurePath, output_extension:str|None, **metadata_overrides)->RipReport:
	logger = logging.getLogger(__name__)
	output_dir = PurePath(output_dir)
	input_dir = PurePath(input_dir)
	if output_extension != None:
		output_extension = str(output_extension)
	metadata_args = override_media_metadata(**metadata_overrides)
	conversions = dict()

	logger.info(f'beginning rip from {input_dir} to {output_dir} with {output_extension} output type and following metadata overrides: {"\n".join(metadata_overrides)}')
	start_time = time.perf_counter()
	for input_entry in scan_for_audio(input_dir):
		input_path = input_entry.path
		output_path = os.path.join(output_dir, change_file_extension(input_entry.name, output_extension))
		copy_media(output_path, input_path, **metadata_args)
		conversions[input_path]=output_path
		logger.debug(f'copied {input_path} to {output_path}')
	duration = time.perf_counter()-start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')

	return RipReport(output_dir, input_dir, output_extension, metadata_overrides, metadata_args, conversions, duration)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}

	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} starting...')
	report = rip_sequential(OUTPUT_DIR, INPUT_DIR, '.mp3', **METADATA_OVERRIDES)
	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} complete\n{report}')