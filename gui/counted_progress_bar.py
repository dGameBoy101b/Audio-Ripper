from logging import getLogger
from tkinter import ttk, DoubleVar, IntVar
from typing import Callable

class CountedProgressbar(ttk.Frame):

	def default_to_string(value:float|int, max:float|int)->str:
		return f'{value}/{max}'

	def __init__(self, value:DoubleVar|IntVar, maximum:float|int, to_string:Callable[[float|int, float|int], str]=None, master:ttk.Widget=None):
		super().__init__(master)

		self.value_variable = value
		self.maximum = maximum
		self.to_string = CountedProgressbar.default_to_string if to_string is None else to_string
		self.progressbar = ttk.Progressbar(self, mode='determinate', maximum=maximum, variable=self.value_variable)
		self.counter = ttk.Label(self, text=self.to_string(self.value_variable.get(), self.maximum))
		self.__callback_name = self.value_variable.trace_add('write', self.__update)

		self.progressbar.grid(column=0, row=0, sticky='EW')
		self.counter.grid(column=1, row=0)
		self.columnconfigure(0, weight=1)

	def __update(self, var, index, mode):
		logger = getLogger(__name__)
		value = self.value_variable.get()
		self.counter['text'] = self.to_string(value, self.maximum)
		if value > self.maximum:
			logger.warning(f'progress value exceeded maximum: {value} / {self.maximum}')

	def destroy(self):
		self.value_variable.trace_remove('write', self.__callback_name)
		return super().destroy()