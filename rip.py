import logging
from rip_args import RipArgs
from rip_report import RipReport
from enum import Enum

class RipStrategy(Enum):
	THREADED = 'threaded'
	SEQUENTIAL = 'sequential'
	MULTIPROCESSING = 'multiprocessing'

def rip(args: RipArgs, strategy:RipStrategy=RipStrategy.THREADED)->RipReport:
	logger = logging.getLogger(__name__)

	if strategy == RipStrategy.SEQUENTIAL:
		from sequential_rip import rip_sequential
		logger.debug('ripping sequentially')
		return rip_sequential(args)
	
	if strategy == RipStrategy.MULTIPROCESSING:
		from multiprocessing_rip import rip_multiprocessed
		logger.debug('ripping with multiprocessing')
		return rip_multiprocessed(args)
	
	from threaded_rip import rip_threaded
	logger.debug('ripping with threading')
	return rip_threaded(args)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}
	ARGS=RipArgs(OUTPUT_DIR, INPUT_DIR, '.mp3', METADATA_OVERRIDES)

	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} starting...')
	report = rip(ARGS, 'sequential')
	print(f'{INPUT_DIR} -sequential rip-> {OUTPUT_DIR} complete\n{report}')
	input('ready for next test case?')

	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} starting...')
	report = rip(ARGS, 'threaded')
	print(f'{INPUT_DIR} -threaded rip-> {OUTPUT_DIR} complete\n{report}')
	input('ready for next test case?')

	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} starting...')
	report = rip(ARGS, 'multiprocessing')
	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} complete\n{report}')