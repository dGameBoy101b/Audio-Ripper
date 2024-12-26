from logging import getLogger
from tkinter import Misc, StringVar
from tkinter.ttk import Button, Entry, Frame

class MetadataOverrideItem(Frame):

	def __init__(self, master:Misc=None, key:str='', value:str='', **kwargs):
		super().__init__(master, **kwargs)
		self.__create_widgets(key, value)
		self.__configure_grid()

	def __create_widgets(self, key:str, value:str):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.key_variable = StringVar(self, key)
		self.value_variable = StringVar(self, value)
		self.key_entry = Entry(self, textvariable=self.key_variable, width=10)
		self.value_entry = Entry(self, textvariable=self.value_variable, width=20)
		self.remove_button = Button(self, command=self.destroy, text='x', width=2)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.key_entry.grid(column=0, row=0, sticky='EW')
		self.value_entry.grid(column=1, row=0, sticky='EW')
		self.remove_button.grid(column=2, row=0)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)
		logger.debug(f'grid configured: {self}')

	def get(self)->tuple[str,str]:
		return (self.key_variable.get(), self.value_variable.get())
	
	def get_key(self)->str:
		return self.key_variable.get()
	
	def get_value(self)->str:
		return self.value_variable.get()