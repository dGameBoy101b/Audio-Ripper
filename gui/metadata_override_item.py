from tkinter import ttk
from typing import Callable

class MetadataOverrideItem:

	def __init__(self, master:ttk.Widget=None, on_remove:Callable[['MetadataOverrideItem'],None]=None):
		self.on_remove = on_remove
		self.key_entry = ttk.Entry(master, width=10)
		self.value_entry = ttk.Entry(master, width=20)
		self.remove_button = ttk.Button(master, command=self.__remove, text='-', width=2)

	def __remove(self):
		if self.on_remove:
			self.on_remove(self)
		self.key_entry.destroy()
		self.value_entry.destroy()
		self.remove_button.destroy()

	def get(self)->str:
		return f'{self.key_entry.get()}={self.value_entry.get()}'