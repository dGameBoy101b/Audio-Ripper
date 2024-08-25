from rip_report import RipReport
import logging
from scan_for_audio import scan_for_audio
from override_media_metadata import override_media_metadata
from to_mp3 import change_file_extension
from copy_media import copy_media
from os import DirEntry
import os.path
import multiprocessing.pool
from dataclasses import dataclass
from collections.abc import Iterable
import time

@dataclass(frozen=True)
class __MultiprocessArgs:
	input_path:str
	output_dir:str
	output_extension:str
	metadata_args: dict

def __copy(args:__MultiprocessArgs):
		logger = logging.getLogger(__name__)
		input_path = args.input_path
		output_path = os.path.join(args.output_dir, change_file_extension(os.path.basename(args.input_path), args.output_extension))
		logger.debug(f'copying {input_path} to {output_path}')
		copy_media(output_path, input_path, **args.metadata_args)
		logger.debug(f'copied {input_path} to {output_path}')
		return (input_path, output_path)

def rip_multiprocessed(output_dir:str, input_dir:str, output_extension:str, **metadata_overrides)->RipReport:
	logger = logging.getLogger(__name__)
	metadata_args = override_media_metadata(**metadata_overrides)

	def generate_args(input_entries:Iterable[DirEntry])->Iterable[__MultiprocessArgs]:
		for input_entry in input_entries:
			yield __MultiprocessArgs(input_entry.path, output_dir, output_extension, metadata_args)

	logger.info(f'beginning rip from {input_dir} to {output_dir} with {output_extension} output type and following metadata overrides: {"\n".join(metadata_overrides)}')
	start_time = time.perf_counter()
	logger.debug('creating process pool...')
	with multiprocessing.pool.Pool() as pool:
		logger.debug('mapping tasks...')
		conversions = pool.map(__copy, generate_args(scan_for_audio(input_dir)))
		logger.debug('saving conversions')
		conversions = dict(conversions)
	duration = time.perf_counter()-start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')

	return RipReport(output_dir, input_dir, output_extension, metadata_overrides, metadata_args, conversions, duration)

if __name__ =='__main__':
	import sys
	logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
	OUTPUT_DIR='./test_out'
	INPUT_DIR='./test_dir'
	METADATA_OVERRIDES={'test':'foobar', 'year':2024}

	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} starting...')
	report = rip_multiprocessed(OUTPUT_DIR, INPUT_DIR, '.mp3', **METADATA_OVERRIDES)
	print(f'{INPUT_DIR} -multiprocessing rip-> {OUTPUT_DIR} complete\n{report}')