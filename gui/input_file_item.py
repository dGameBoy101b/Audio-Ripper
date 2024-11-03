from tkinter import ttk
from os import PathLike
import tkinter
from logging import getLogger
from os.path import abspath

class InputFileItem(ttk.Frame):

	def __init__(self, path: PathLike, master=None, *, on_remove=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input file item')

		self.path = path
		self.on_remove = on_remove
		logger.debug('setup input file item variables')

		self.variable = tkinter.StringVar(master=self, value=abspath(path))
		self.text = ttk.Entry(self, textvariable=self.variable, width=30, state='readonly')
		self.remove_button = ttk.Button(self, text='x', command=self.remove, width=2)
		logger.debug('created input file item children')

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.columnconfigure(0, weight=1)
		logger.debug('layed out input file item')

	def remove(self):
		logger = getLogger(__name__)
		self.on_remove(self)
		self.destroy()
		logger.debug(f'removed input path: {self.path}')

	def get(self)->PathLike:
		return self.path