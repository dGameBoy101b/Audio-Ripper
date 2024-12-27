from logging import getLogger
from os.path import abspath, join, basename
from tkinter import Misc
from tkinter.ttk import Button, LabelFrame
from typing import Iterable

from ..audio_copy_job import AudioCopyJob
from ..job_executor import JobExecutor
from ..change_file_extension import change_file_extension
from .. override_media_metadata import override_media_metadata

from .vertical_box import VerticalBox
from .output_file_item import OutputFileItem
from .input_files_frame import InputFilesFrame
from .settings_frame import SettingsFrame
from .widget_exploration import explore_descendants

class OutputFilesFrame(LabelFrame):
	def __init__(self, job_executor:JobExecutor, input_files:InputFilesFrame, settings:SettingsFrame, master:Misc=None, **kwargs):
		super().__init__(master, **kwargs, text='Output Files')
		self.job_executor = job_executor
		self.input_files = input_files
		self.settings = settings
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.rip_button = Button(self, text='Start Rip', command=self.start_rip)
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.rip_button.grid(row=0, column=0, sticky='EW')
		self.content_box.grid(row=1, column=0, sticky='NSEW')
		self.content_box.content.columnconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')

	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.content_box.content.winfo_children():
			if item.winfo_exists():
				item.grid(row=0, column=0, sticky='EW')
				row += 1
		logger.debug(f'layed out {row} output file items')

	def __create_jobs(self)->Iterable[AudioCopyJob]:
		logger = getLogger(__name__)
		logger.debug(f'creating jobs... {self}')
		files = tuple(self.input_files.get())
		output_dir = self.settings.directory.get()
		logger.debug(f'output directory: {abspath(output_dir)}')
		output_extension = self.settings.file_extension.get()
		logger.debug(f'output extension: {output_extension}')
		metadata_overrides = self.settings.metadata_overrides.get()
		logger.debug(f'metadata overrides: {''.join([f'{key}={metadata_overrides[key]}\n' for key in metadata_overrides])}')
		output_args = override_media_metadata(**metadata_overrides)
		for input_path in files:
			output_path = abspath(join(output_dir, change_file_extension(basename(input_path), output_extension)))
			logger.debug(f'created job {input_path}->{output_path}: {self}')
			yield AudioCopyJob(output_path, input_path, output_args)

	def __create_items(self)->list[OutputFileItem]:
		logger = getLogger(__name__)
		logger.debug(f'creating items... {self}')
		items = list()
		for job in self.__create_jobs():
			self.job_executor.jobs.put(job)
			item = OutputFileItem(job.output_path, self.content_box.content)
			items.append(item)
			for child in explore_descendants(item):
				self.content_box.bind_scroll_forwarding(child)
			self.__layout_items()
			self.update()
		logger.debug(f'{len(items)} items created')
		return items
		
	def start_rip(self):
		logger = getLogger(__name__)
		logger.info('starting rip...')
		items = self.__create_items()
		futures = self.job_executor.start_jobs()
		assert len(items) == len(futures)
		for index in range(len(items)):
			items[index].started(futures[index])
		logger.info(f'started {len(items)} rip jobs')
