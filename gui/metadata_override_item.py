from tkinter import Misc, StringVar
from tkinter.ttk import Button, Entry, Frame

class MetadataOverrideItem(Frame):

	def __init__(self, master:Misc=None, key:str='', value:str='', **kwargs):
		super().__init__(master, **kwargs)

		self.key_variable = StringVar(self, key)
		self.value_variable = StringVar(self, value)

		self.key_entry = Entry(self, textvariable=self.key_variable, width=10)
		self.value_entry = Entry(self, textvariable=self.value_variable, width=20)
		self.remove_button = Button(self, command=self.destroy, text='x', width=2)

		self.key_entry.grid(column=0, row=0, sticky='EW')
		self.value_entry.grid(column=1, row=0, sticky='EW')
		self.remove_button.grid(column=2, row=0)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)

	def get(self)->tuple[str,str]:
		return (self.key_variable.get(), self.value_variable.get())