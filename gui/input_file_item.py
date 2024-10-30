from tkinter import ttk
from os import PathLike

class InputFileItem(ttk.Frame):

	def __init__(self, path: PathLike, master=None, on_remove=None):
		super().__init__(master)

		self.path = path
		self.on_remove = on_remove

		self.text = ttk.Label(self, text=str(path), width=20)
		self.remove_button = ttk.Button(self, text='x', command=self.remove)

		self.text.grid(column=0, row=0)
		self.remove_button.grid(column=1, row=0)
		self.columnconfigure(0, weight=1)

	def remove(self):
		self.on_remove(self)
		self.destroy()
		print(f'removed input path: {self.path}')

	def get(self)->PathLike:
		return self.path