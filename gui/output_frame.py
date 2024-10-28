from tkinter import ttk

class OutputFrame(ttk.LabelFrame):

	def __init__(self, master=None):
		super().__init__(master, text='Output')
		self._create_child_widgets()

	def _create_child_widgets(self):
		placeholder = ttk.Label(self, text='Output Placeholder')
		placeholder.grid()
