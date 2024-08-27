from rip_args import RipArgs
from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from change_file_extension import change_file_extension
from copy_media import copy_media
import os.path
import time

def rip_sequential(args:RipArgs)->RipReport:
	logger = logging.getLogger(__name__)
	conversions = dict()

	logger.info(f'beginning rip from {args.input_dir} to {args.output_dir} with {args.output_extension} output type and following metadata overrides: {"\n".join(args.metadata_overrides)}')
	start_time = time.perf_counter()
	for input_entry in scan_for_audio(args.input_dir):
		input_path = input_entry.path
		output_path = args.output_path(input_path)
		copy_media(output_path, input_path, **args.output_args)
		conversions[input_path]=output_path
		logger.debug(f'copied {input_path} to {output_path}')
	duration = time.perf_counter()-start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')

	return RipReport(args.output_dir, args.input_dir, args.output_extension, args.metadata_overrides, args.output_args, conversions, duration)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}
	ARGS=RipArgs(OUTPUT_DIR, INPUT_DIR, '.mp3', METADATA_OVERRIDES)

	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} starting...')
	report = rip_sequential(ARGS)
	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} complete\n{report}')