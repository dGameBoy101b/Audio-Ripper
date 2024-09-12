from rip_args import RipArgs
from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from change_file_extension import change_file_extension
from copy_media import copy_media
from os import DirEntry
import os.path
import threading
import time

def rip_threaded(args:RipArgs)->RipReport:
	logger = logging.getLogger(__name__)
	conversions = dict()
	
	def copy(input_entry:DirEntry):
		input_path = input_entry.path
		output_path = args.output_path(input_path)
		copy_media(output_path, input_path, **args.output_args)
		conversions[input_path]=output_path
		logger.debug(f'copied {input_path} to {output_path}')

	logger.info(f'beginning rip from {args.input_dir} to {args.output_dir} with {args.output_extension} output type and following metadata overrides: {"\n".join(args.metadata_overrides)}')
	start_time = time.perf_counter()
	logger.debug('creating threads...')
	threads = [threading.Thread(target=copy, args=(entry,)) for entry in scan_for_audio(args.input_dir)]
	logger.debug('starting threads...')
	for thread in threads:
		thread.start()
	index = 0
	for thread in threads:
		logger.debug(f'waiting for threads {index}/{len(threads)}')
		thread.join()
		index += 1
	duration = time.perf_counter()-start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')

	return RipReport(args, conversions, duration)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}
	ARGS=RipArgs(OUTPUT_DIR, INPUT_DIR, '.mp3', METADATA_OVERRIDES)

	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} starting...')
	report = rip_threaded(ARGS)
	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} complete\n{report}')