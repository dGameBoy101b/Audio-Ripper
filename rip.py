from concurrent.futures import Executor, Future, wait
import logging
import time

from .copy_media import copy_media
from .rip_args import RipArgs
from .rip_report import RipReport
from .scan_for_audio import scan_for_audio

def rip(args:RipArgs, executor:Executor)->RipReport:
	logger = logging.getLogger(__name__)
	conversions = dict()

	logger.info(f'beginning rip from {args.input_dir} to {args.output_dir} with {args.output_extension} output type and following metadata overrides: {"\n".join(args.metadata_overrides)}')
	start_time = time.perf_counter()
	futures:list[Future] = list()

	logger.debug('submitting jobs...')
	for input_path in scan_for_audio(args.input_dir):
		output_path = args.output_path(input_path)
		conversions[input_path] = output_path
		future = executor.submit(copy_media, output_path, input_path, **args.output_args)
		futures.append(future)

	logger.debug(f'waiting for {len(futures)} futures...')
	wait(futures)

	duration = time.perf_counter() - start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')
	return RipReport(args, conversions, duration)