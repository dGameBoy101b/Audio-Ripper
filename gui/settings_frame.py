from logging import getLogger
from tkinter import ttk

from .output_directory_frame import OutputDirectoryFrame
from .file_extension_frame import FileExtensionFrame
from .metadata_overrides_frame import MetadataOverridesFrame

class SettingsFrame(ttk.LabelFrame):

	def __init__(self, master=None):
		super().__init__(master, text='Settings')
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.file_extension = FileExtensionFrame(self)
		self.directory = OutputDirectoryFrame(self)
		self.metadata_overrides = MetadataOverridesFrame(self)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.directory.grid(row=0, column=0, sticky='EW')
		self.file_extension.grid(row=1, column=0, sticky='EW')
		self.metadata_overrides.grid(row=2, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(2, weight=1)
		logger.debug(f'grid configured: {self}')

