from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from override_media_metadata import override_media_metadata
from to_mp3 import change_file_extension
from copy_media import copy_media
from os import DirEntry
import os.path
import threading

def rip_threaded(output_dir:str, input_dir:str, output_extension:str, **metadata_overrides)->RipReport:
	logger = logging.getLogger(__name__)
	metadata_args = override_media_metadata(**metadata_overrides)
	conversions = dict()
	
	def copy(input_entry:DirEntry):
		input_path = input_entry.path
		output_path = os.path.join(output_dir, change_file_extension(input_entry.name, output_extension))
		copy_media(output_path, input_path, **metadata_args)
		conversions[input_path]=output_path
		logger.debug(f'copied {input_path} to {output_path}')

	logger.info(f'beginning rip from {input_dir} to {output_dir} with {output_extension} output type and following metadata overrides: {"\n".join(metadata_overrides)}')
	logger.debug('creating threads...')
	threads = [threading.Thread(target=copy, args=(entry,)) for entry in scan_for_audio(input_dir)]
	logger.debug('starting threads...')
	for thread in threads:
		thread.start()
	index = 0
	for thread in threads:
		logger.debug(f'waiting for threads {index}/{len(threads)}')
		thread.join()
		index += 1
	logger.info(f'ripped {len(conversions)} audio files')

	return RipReport(output_dir, input_dir, output_extension, metadata_overrides, metadata_args, conversions)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}

	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} starting...')
	report = rip_threaded(OUTPUT_DIR, INPUT_DIR, '.mp3', **METADATA_OVERRIDES)
	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} complete\n{report}')