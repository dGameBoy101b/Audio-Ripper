from tkinter import ttk
from typing import Callable, Self

class MetadataOverrideItem(ttk.Frame):

	def __init__(self, master:ttk.Widget=None, on_remove:Callable[['MetadataOverrideItem'],None]=None):
		super().__init__(master)
		self.on_remove = on_remove
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)
		self.key_entry = ttk.Entry(self)
		self.key_entry.grid(column=0, row=0, sticky='EW')
		self.value_entry = ttk.Entry(self)
		self.value_entry.grid(column=1, row=0, sticky='EW')
		self.remove_button = ttk.Button(self, command=self.__remove, text='-', width=2)
		self.remove_button.grid(column=2, row=0)

	def __remove(self):
		if self.on_remove:
			self.on_remove(self)
		self.destroy()

	def get(self)->str:
		return f'{self.key_entry.get()}={self.value_entry.get()}'