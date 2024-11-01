from rip_args import RipArgs
from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from copy_media import copy_media
from os import DirEntry
import multiprocessing.pool
from dataclasses import dataclass
from collections.abc import Iterable
import time
from pathlib import PurePath

@dataclass(frozen=True)
class __MultiprocessArgs:
	input_path: PurePath
	rip_args: RipArgs

def __copy(args:__MultiprocessArgs):
		logger = logging.getLogger(__name__)
		input_path = args.input_path
		output_path = args.rip_args.output_path(input_path)
		logger.debug(f'copying {input_path} to {output_path}')
		copy_media(output_path, input_path, **args.rip_args.output_args)
		logger.debug(f'copied {input_path} to {output_path}')
		return (input_path, output_path)

def rip_multiprocessed(args:RipArgs)->RipReport:
	logger = logging.getLogger(__name__)

	def generate_args(input_entries:Iterable[DirEntry])->Iterable[__MultiprocessArgs]:
		for input_entry in input_entries:
			yield __MultiprocessArgs(PurePath(input_entry.path), args)

	logger.info(f'beginning rip from {args.input_dir} to {args.output_dir} with {args.output_extension} output type and following metadata overrides: {"\n".join(args.metadata_overrides)}')
	start_time = time.perf_counter()
	logger.debug('creating process pool...')
	with multiprocessing.pool.Pool() as pool:
		logger.debug('mapping tasks...')
		conversions = pool.map(__copy, generate_args(scan_for_audio(args.input_dir)))
		logger.debug('saving conversions...')
		conversions = dict(conversions)
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

	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} starting...')
	report = rip_multiprocessed(ARGS)
	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} complete\n{report}')