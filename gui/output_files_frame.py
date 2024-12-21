from logging import getLogger
from tkinter import Misc
from tkinter.ttk import Button, LabelFrame

from .vertical_box import VerticalBox

class OutputFilesFrame(LabelFrame):
	def __init__(self, master:Misc=None, **kwargs):
		super().__init__(master, **kwargs, text='Output Files')
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.rip_button = Button(self, text='Start Rip', command=self.start_rip)
		self.content_box = VerticalBox(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.rip_button.grid(row=0, column=0, sticky='EW')
		self.content_box.grid(row=1, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')
		
	def start_rip(self):
		logger = getLogger(__name__)
		logger.info('starting rip...')
		logger.info('rip complete')