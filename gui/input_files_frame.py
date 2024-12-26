from logging import getLogger
from os import PathLike, fspath
from os.path import abspath
from tkinter import Event, Misc
from tkinter.ttk import Button, LabelFrame
from tkinter.filedialog import askopenfilenames
from typing import Callable, Iterable

from .vertical_box import VerticalBox
from .input_file_item import InputFileItem
from .widget_exploration import explore_descendants

class InputFilesFrame(LabelFrame):
	def __init__(self, is_audio:Callable[[PathLike],bool], master:Misc=None, **kwargs):
		super().__init__(master, **kwargs, text='Input Files')
		self.files: list[PathLike] = list()
		self.is_audio = is_audio
		self.__destroy_bindings = dict()
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.add_files_button = Button(self, command=self.ask_files, text='Add Files')
		self.clear_files_button = Button(self, command=self.remove_all_files, text='Clear Files')
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.add_files_button.grid(row=0, column=0, sticky='EW')
		self.clear_files_button.grid(row=0, column=1, sticky='EW')
		self.content_box.grid(row=1, column=0, columnspan=2, sticky='NSEW')
		self.content_box.content.columnconfigure(0, weight=1)
		self.columnconfigure([0,1], weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')
	
	def __file_item_destroyed(self, event:Event):
		self.remove_file_item(event.widget)

	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.content_box.content.winfo_children():
			if not item.winfo_exists():
				continue
			item.grid(column=0, row=row, sticky='EW')
			row += 1
		logger.info(f'layed out {row} input file items')
		self.update()

	def ask_files(self)->int:
		logger = getLogger(__name__)
		logger.info('opening input files dialog')
		filenames = askopenfilenames(title='Input Audio Files')
		if filenames == '':
			logger.info('no input files selected')
			return 0
		count = 0
		for filename in filenames:
			try:
				self.add_file(filename)
				count += 1
			except BaseException as x:
				logger.warning(f'invalid input file skipped: {x}', exc_info=x)
		logger.info(f'added {count}/{len(filenames)} selected input files')
		return count

	def add_file(self, filename:PathLike):
		logger = getLogger(__name__)
		if abspath(filename) in self.files:
			raise ValueError(f'duplicate input file: {fspath(filename)}')
		if not self.is_audio(filename):
			raise ValueError(f'non-audio input file: {fspath(filename)}')
		item = InputFileItem(filename, self.content_box.content)
		binding = item.bind('<Destroy>', self.__file_item_destroyed)
		self.__destroy_bindings[item] = binding
		for widget in explore_descendants(item):
			self.content_box.bind_scroll_forwarding(widget)
		self.files.append(abspath(filename))
		logger.info(f'audio input file added: {fspath(filename)}')
		self.__layout_items()

	def remove_file(self, filename:PathLike):
		path = abspath(filename)
		for item in self.content_box.content.winfo_children():
			if isinstance(item, InputFileItem) and abspath(item.get()) == path:
				self.remove_file_item(item)
				return
		raise ValueError(f'input file item not found: {path}')

	def remove_file_item(self, item:InputFileItem):
		logger = getLogger(__name__)
		path = abspath(item.get())
		self.files.remove(path)
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		logger.info(f'input file removed: {path}')
		self.__layout_items()

	def remove_all_files(self):
		logger = getLogger(__name__)
		to_destroy = list(self.content_box.content.winfo_children())
		self.files.clear()
		for item in to_destroy:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
			del self.__destroy_bindings[item]
			item.destroy()
		logger.info(f'cleared all {len(to_destroy)} files')
		self.__layout_items()

	def get(self)->Iterable[PathLike]:
		return self.files
	
	def destroy(self):
		for item in explore_descendants(self.content_box.content):
			if item in self.__destroy_bindings:
				item.unbind('<Destroy>', self.__destroy_bindings[item])
		self.__destroy_bindings.clear()
		self.files.clear()
		return super().destroy()