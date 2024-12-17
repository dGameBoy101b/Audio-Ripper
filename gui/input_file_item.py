from tkinter import ttk
from os import PathLike
import tkinter
from logging import getLogger
from os.path import abspath

class InputFileItem(tkinter.Frame):

	def __init__(self, path: PathLike, master=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input file item')

		self.variable = tkinter.StringVar(master=self, value=abspath(path))
		self.text = ttk.Entry(self, textvariable=self.variable, width=30, state='readonly')
		self.remove_button = ttk.Button(self, text='x', command=self.destroy, width=2)
		logger.debug('created input file item children')

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.columnconfigure(0, weight=1)
		logger.debug('layed out input file item')

	def get(self)->PathLike:
		return self.variable.get()