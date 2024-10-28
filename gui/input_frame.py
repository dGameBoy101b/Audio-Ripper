from tkinter import ttk

class InputFrame(ttk.Labelframe):

	def __init__(self, master=None):
		super().__init__(master, text='Input')
		self._create_child_widgets()

	def _create_child_widgets(self):
		placeholder = ttk.Label(self, text='Input Placeholder')
		placeholder.grid()
