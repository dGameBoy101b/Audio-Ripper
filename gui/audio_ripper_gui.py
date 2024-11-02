from tkinter import ttk
from .settings_frame import SettingsFrame
from .input_frame import InputFrame
from .output_frame import OutputFrame
from .async_tk import AsyncTk
import logging
from os import path

class AudioRipperGUI(ttk.Frame):

	def __init__(self, master=None):
		logger = logging.getLogger(__name__)
		ttk.Frame.__init__(self, master)
		logger.debug('created audio ripper gui')

		self.settingsFrame = SettingsFrame(self)
		self.inputFrame = InputFrame(self)
		self.outputFrame = OutputFrame(self)
		logger.debug('created audio ripper gui children')

		self.grid(sticky='NSEW')
		self.rowconfigure(0, weight=1)
		self.columnconfigure([0,1,2], weight=1)
		self.settingsFrame.grid(column=0, row=0, sticky='NSEW')
		self.inputFrame.grid(column=1, row=0, sticky='NSEW')
		self.outputFrame.grid(column=2, row=0, sticky='NSEW')
		logger.debug('layed out audio ripper gui')

	def configure_window(self):
		logger = logging.getLogger(__name__)
		window = self.winfo_toplevel()
		window.title('Audio Ripper')
		window.columnconfigure(0, weight=1)
		window.rowconfigure(0, weight=1)
		logger.debug(f'configured audio ripper gui window: {type(window)}')

def main():
	logging.basicConfig(filename=path.join(path.dirname(__file__), "./rip_gui.log"), filemode='w', level=logging.DEBUG, style="{", format="[{asctime}]{levelname}:{name}:{msg}")
	logger = logging.getLogger(__name__)
	logger.debug('configured logging')

	#tk = AsyncTk()
	app = AudioRipperGUI()
	app.configure_window()
	logger.debug('configured audio ripper gui')

	logger.debug('starting audio ripper gui main loop...')
	app.mainloop()

if __name__ == '__main__':
	main()