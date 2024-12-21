from os import PathLike
from tkinter.ttk import Labelframe, PanedWindow
from logging import getLogger

from ..audio_scanner import AudioScanner

from .input_files_frame import InputFilesFrame
from .input_scans_frame import InputScansFrame

class InputFrame(Labelframe):

	def __init__(self, master=None, **kwargs):
		super().__init__(master, text='Input', **kwargs)
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.panes = PanedWindow(self, orient='horizontal')
		scanner = AudioScanner()
		self.files_frame = InputFilesFrame(scanner.is_audio, self.panes)
		self.scans_frame = InputScansFrame(self.files_frame, scanner, self.panes)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.panes.grid(row=0, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.panes.add(self.scans_frame)
		self.panes.add(self.files_frame)
		logger.debug(f'grid configured: {self}')

	def get(self)->list[PathLike]:
		return self.files_frame.get()