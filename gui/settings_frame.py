from tkinter import ttk
from file_extension_frame import FileExtensionFrame

class SettingsFrame(ttk.LabelFrame):

	def __init__(self, master=None):
		super().__init__(master, text='Settings')
		self.columnconfigure(0, weight=1)
		self._create_child_widgets()

	def _create_child_widgets(self):
		self.file_extension = FileExtensionFrame(self)
		self.file_extension.grid(column=0, row=0, sticky='EW')
