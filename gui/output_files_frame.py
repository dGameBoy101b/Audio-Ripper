from concurrent.futures import Executor, Future
from logging import getLogger
from os import PathLike
from os.path import abspath, join, basename, splitext
from tkinter import Misc
from tkinter.ttk import Button, LabelFrame
from typing import Iterable, Tuple

from ..change_file_extension import change_file_extension
from ..override_media_metadata import override_media_metadata
from ..copy_media import copy_media

from .vertical_box import VerticalBox
from .output_file_item import OutputFileItem
from .input_files_frame import InputFilesFrame
from .settings_frame import SettingsFrame
from .widget_exploration import explore_descendants

StrPath = PathLike|str

class OutputFilesFrame(LabelFrame):
	def __init__(self, executor:Executor, input_files:InputFilesFrame, settings:SettingsFrame, master:Misc|None=None, **kwargs):
		super().__init__(master, **kwargs, text='Output Files')
		self.executor = executor
		self.input_files = input_files
		self.settings = settings
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.preview_button = Button(self, text='Preview', command=self.show_preview)
		self.rip_button = Button(self, text='Start Rip', command=self.start_rip)
		self.clear_button = Button(self, text='Clear Ouput', command=self.clear)
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.preview_button.grid(row=0, column=0, sticky='EW')
		self.rip_button.grid(row=0, column=1, sticky='EW')
		self.clear_button.grid(row=0, column=2, sticky='EW')
		self.content_box.grid(row=1, column=0, columnspan=3, sticky='NSEW')
		self.content_box.content.columnconfigure(0, weight=1)
		self.columnconfigure([0,1,2], weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')

	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.content_box.content.winfo_children():
			if item.winfo_exists():
				item.grid(row=row, column=0, sticky='EW')
				row += 1
		logger.debug(f'layed out {row} output file items')

	def input_paths(self)->Iterable[StrPath]:
		return self.input_files.get()

	def output_paths(self, input_paths:Iterable[StrPath])->Iterable[StrPath]:
		logger = getLogger(__name__)
		logger.debug(f'generating output paths... {self}')
		output_dir = self.settings.directory.get()
		logger.debug(f'output directory: {abspath(output_dir)}')
		output_extension = self.settings.file_extension.get()
		logger.debug(f'output extension: {output_extension}')
		input_paths = set(input_paths)
		output_paths:set[StrPath] = set()
		for input_path in input_paths:
			output_path = abspath(join(output_dir, change_file_extension(basename(input_path), output_extension)))
			if output_path in output_paths:
				old = output_path
				root, ext = splitext(output_path)
				count = 1
				while output_path in output_paths | (input_paths - {old}):
					output_path = f'{root}{count}{ext}'
					count += 1
				logger.warning(f'renamed duplicate output path: {input_path} -> {old} -> {output_path}')
			logger.debug(f'generated output path: {input_path} -> {output_path}')
			output_paths.add(output_path)
			yield output_path

	def __submit_jobs(self, input_paths:Iterable[StrPath], output_paths:Iterable[StrPath])->Iterable[Future]:
		logger = getLogger(__name__)
		logger.debug(f'submitting jobs... {self}')
		metadata_overrides = self.settings.metadata_overrides.get()
		logger.debug(f'metadata overrides: {''.join([f'{key}={metadata_overrides[key]}\n' for key in metadata_overrides])}')
		output_args = override_media_metadata(**metadata_overrides)
		for input_path, output_path in zip(input_paths, output_paths, strict=True):
			future = self.executor.submit(copy_media, output_path, input_path, **output_args)
			logger.debug(f'submitted job {input_path}->{output_path}: {self}')
			yield future

	def __create_items(self, output_paths:Iterable[StrPath])->list[OutputFileItem]:
		logger = getLogger(__name__)
		logger.debug(f'creating items... {self}')
		items = list()
		for path in output_paths:
			item = OutputFileItem(path, master=self.content_box.content)
			items.append(item)
			logger.debug(f'created item: {path} {item}')
			for child in explore_descendants(item):
				self.content_box.bind_scroll_forwarding(child)
			self.__layout_items()
			self.update()
		logger.debug(f'{len(items)} items created')
		return items
	
	def show_preview(self):
		logger = getLogger(__name__)
		logger.info('generating preview...')
		self.clear()
		self.__create_items(self.output_paths(self.input_paths()))
		logger.info('preview generated')
		
	def start_rip(self):
		logger = getLogger(__name__)
		logger.info('starting rip...')
		self.clear()
		input_paths = tuple(self.input_paths())
		output_paths = tuple(self.output_paths(input_paths))
		items = self.__create_items(output_paths)
		futures = self.__submit_jobs(input_paths, output_paths)
		for item, future in zip(items, futures, strict=True):
			item.started(future)
		logger.info(f'started {len(items)} rip jobs')

	def clear(self):
		logger = getLogger(__name__)
		logger.info('clearing output...')
		count = 0
		for widget in self.content_box.content.winfo_children():
			if not widget.winfo_exists():
				continue
			widget.destroy()
			count += 1
		self.__layout_items()
		logger.info(f'cleared {count} output items')
