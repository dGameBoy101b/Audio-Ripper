from logging import getLogger
from tkinter import Misc
from tkinter.ttk import LabelFrame

from .vertical_box import VerticalBox

class ConversionsFrame(LabelFrame):
	def __init__(self, master:Misc=None, **kwargs):
		super().__init__(master, **kwargs, text='Conversions')
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.content_box.grid(row=0, column=0)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		logger.debug(f'grid configured: {self}')