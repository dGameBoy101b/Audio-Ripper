from concurrent.futures import Executor, wait
import logging
import time
from .audio_copy_job import AudioCopyJob
from .audio_scanner import AudioScanner
from .job_executor import JobExecutor
from .rip_args import RipArgs
from .rip_report import RipReport


def rip_jobs(args:RipArgs, executor:Executor)->RipReport:
	logger = logging.getLogger(__name__)
	conversions = dict()

	logger.info(f'beginning rip from {args.input_dir} to {args.output_dir} with {args.output_extension} output type and following metadata overrides: {"\n".join(args.metadata_overrides)}')
	start_time = time.perf_counter()
	with JobExecutor(executor) as job_executor:

		logger.debug('creating jobs...')
		with AudioScanner(args.input_dir) as scanner:
			for audio_path in scanner:
				output_path = args.output_path(audio_path)
				conversions[audio_path] = output_path
				job = AudioCopyJob(output_path, audio_path, args.output_args)
				job_executor.jobs.put(job)
		
		logger.debug(f'starting {job_executor.jobs.qsize()} jobs...')
		futures = job_executor.start_jobs()

		logger.debug(f'waiting for {len(futures)} jobs...')
		wait(futures)

	duration = time.perf_counter()-start_time
	logger.info(f'ripped {len(conversions)} audio files in {duration} seconds')
	return RipReport(args, conversions, duration)