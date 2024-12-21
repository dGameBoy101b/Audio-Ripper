from logging import getLogger
from tkinter.ttk import Labelframe, Button

from .conversions_frame import ConversionsFrame

class OutputFrame(Labelframe):

	def __init__(self, master=None):
		super().__init__(master, text='Output')
		self.__create_widgets()
		self.__config_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.rip_button = Button(self, text='Start Rip', command=self.start_rip)
		self.conversions_frame = ConversionsFrame(self)
		logger.debug(f'widgets created: {self}')

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.rip_button.grid(row=0, column=0, sticky='EW')
		self.conversions_frame.grid(row=1, column=0, sticky='NSEW')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		logger.debug(f'grid configured: {self}')

	def start_rip(self):
		logger = getLogger(__name__)
		logger.info('starting rip...')
		logger.info('rip complete')