import logging.config
from tkinter import ttk
from .async_tk import AsyncTk
from .settings_frame import SettingsFrame
from .input_frame import InputFrame
from .output_frame import OutputFrame
import logging
from .configure_logging import config_dict

class AudioRipperGUI(ttk.Panedwindow):

	def __init__(self, master=None):
		logger = logging.getLogger(__name__)
		super().__init__(master, orient='horizontal')
		logger.debug('created audio ripper gui')

		self.settingsFrame = SettingsFrame(self)
		self.inputFrame = InputFrame(self)
		self.outputFrame = OutputFrame(self)
		logger.debug('created audio ripper gui children')

		self.grid(sticky='NSEW')
		self.add(self.settingsFrame, weight=1)
		self.add(self.inputFrame, weight=1)
		self.add(self.outputFrame, weight=1)
		logger.debug('layed out audio ripper gui')

	def configure_window(self):
		logger = logging.getLogger(__name__)
		window = self.winfo_toplevel()
		window.title('Audio Ripper')
		window.columnconfigure(0, weight=1)
		window.rowconfigure(0, weight=1)
		logger.debug(f'configured audio ripper gui window: {type(window)}')

def main():
	logging.config.dictConfig(config_dict)
	logger = logging.getLogger(__name__)
	logger.debug('configured logging')

	tk = AsyncTk()
	app = AudioRipperGUI(tk)
	app.configure_window()
	logger.debug('configured audio ripper gui')

	logger.debug('starting audio ripper gui main loop...')
	app.mainloop()

if __name__ == '__main__':
	main()