from tkinter import ttk

class SettingsFrame(ttk.LabelFrame):

	def __init__(self, master=None):
		super().__init__(master, text='Settings')
		self._create_child_widgets()

	def _create_child_widgets(self):
		placeholder = ttk.Label(self, text='Settings Placeholder')
		placeholder.grid()
