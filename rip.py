import logging
from rip_report import RipReport
from threaded_rip import rip_threaded
from multiprocessing_rip import rip_multiprocessed

def rip(output_dir:str, input_dir:str, output_extension:str='.mp3', strategy:str='threaded', **metadata_overrides)->RipReport:
	logger = logging.getLogger(__name__)
	if strategy == 'multiprocessing':
		logger.debug('ripping with multiprocessing')
		return rip_multiprocessed(output_dir, input_dir, output_extension, **metadata_overrides)
	logger.debug('ripping with threading')
	return rip_threaded(output_dir, input_dir, output_extension, **metadata_overrides)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}

	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} starting...')
	report = rip(OUTPUT_DIR, INPUT_DIR, '.mp3', 'threaded', **METADATA_OVERRIDES)
	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} complete\n{report}')

	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} starting...')
	report = rip(OUTPUT_DIR, INPUT_DIR, '.mp3', 'multiprocessing', **METADATA_OVERRIDES)
	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} complete\n{report}')