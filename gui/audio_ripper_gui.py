from logging import getLogger
from logging.config import dictConfig
from tkinter.ttk import PanedWindow
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

from ..job_executor import JobExecutor
from ..audio_scanner import AudioScanner, is_audio

from .directory_scans_frame import DirectoryScansFrame
from .input_files_frame import InputFilesFrame
from .settings_frame import SettingsFrame
from .output_files_frame import OutputFilesFrame
from .configure_logging import config_dict
from .resiliant_executor import ResiliantExecutor
from .worker_logging import config_dict as worker_config_dict

class AudioRipperGUI(PanedWindow):
	MAX_WORKERS = 60

	def max_workers()->int:
		max_workers = cpu_count()
		if max_workers is None:
			max_workers = 1
		elif max_workers > 1:
			max_workers //= 2
		return min(max_workers, AudioRipperGUI.MAX_WORKERS)

	def __init__(self, master=None):
		super().__init__(master, orient='horizontal')
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.settings_frame = SettingsFrame(self)
		scanner = AudioScanner()
		self.files_frame = InputFilesFrame(is_audio, self)
		self.scans_frame = DirectoryScansFrame(self.files_frame, scanner, self)
		executor = ResiliantExecutor(ProcessPoolExecutor, max_workers=AudioRipperGUI.max_workers(), initializer=dictConfig, initargs=(worker_config_dict,))
		job_executor = JobExecutor(executor)
		self.output_frame = OutputFilesFrame(job_executor, self.files_frame, self.settings_frame, self)
		logger.debug(f'created widgets: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.add(self.settings_frame, weight=1)
		self.add(self.scans_frame, weight=1)
		self.add(self.files_frame, weight=1)
		self.add(self.output_frame, weight=1)
		logger.debug(f'grid configured {self}')

	def configure_window(self):
		logger = getLogger(__name__)
		logger.debug('configuring window...')
		window = self.winfo_toplevel()
		window.title('Audio Ripper')
		window.columnconfigure(0, weight=1)
		window.rowconfigure(0, weight=1)
		self.grid(sticky='NSEW')
		logger.debug(f'window configured: {type(window)}')

def main():
	dictConfig(config_dict)
	logger = getLogger(__name__)
	logger.debug('configured logging')

	#tk = AsyncTk()
	app = AudioRipperGUI()
	app.configure_window()
	logger.debug('configured audio ripper gui')

	logger.debug('starting audio ripper gui main loop...')
	app.mainloop()

if __name__ == '__main__':
	main()