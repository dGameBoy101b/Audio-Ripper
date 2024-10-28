from tkinter import ttk

class FileExtensionFrame(ttk.Frame):

	def __init__(self, master=None):
		super().__init__(master)
		self.columnconfigure(1, weight=1)
		
		self.label = ttk.Label(self, text='File Extension: ')
		self.label.grid(column=0, row=0, sticky='W')

		self.entry = ttk.Entry(self, width=5)
		self.entry.grid(column=1, row=0, sticky='EW')

	def get(self):
		value = self.entry.get()
		if value[0] != '.':
			return '.'+value
		return value
