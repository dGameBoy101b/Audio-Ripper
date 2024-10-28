from tkinter import ttk
from file_extension_frame import FileExtensionFrame
from metadata_overrides_frame import MetadataOverridesFrame

class SettingsFrame(ttk.LabelFrame):

	def __init__(self, master=None):
		super().__init__(master, text='Settings')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.file_extension = FileExtensionFrame(self)
		self.file_extension.grid(column=0, row=0, sticky='EW')
		self.metadata_overrides = MetadataOverridesFrame(self)
		self.metadata_overrides.grid(column=0, row=1, sticky='NSEW')
