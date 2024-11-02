from os import PathLike, scandir, listdir
from tkinter import ttk
from asyncio import create_task
from typing import Callable
from ..scan_for_audio import is_audio, is_directory
from tkinter import StringVar
from logging import getLogger

class InputDirectoryItem(ttk.Frame):

	def __init__(self, path:PathLike, on_remove:Callable[['InputDirectoryItem'],None]=None, on_audio:Callable[[PathLike],None]=None, on_directory:Callable[[PathLike],None]=None, master:ttk.Widget=None, **kwargs):
		logger = getLogger(__name__)
		super().__init__(master, **kwargs)
		logger.debug('created input directory item')

		self.path = path
		self.on_remove = on_remove
		self.on_audio = on_audio
		self.on_directory = on_directory
		logger.debug('setup input directory item variables')

		self.variable = StringVar(self, value=str(path))
		self.text = ttk.Entry(self, textvariable=self.variable, state='readonly', width=30)
		self.remove_button = ttk.Button(self, text='x', command=self.remove, width=2)
		self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', maximum=len(listdir(path)))
		logger.debug('created input directory item children')

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.progress_bar.grid(column=0, columnspan=1, row=1, sticky='EW')
		self.columnconfigure(0, weight=1)
		logger.debug('layed out input directory item')
		
		self.task = create_task(self.__scan())
		logger.info(f'scanning directory: {path}')

	async def __scan(self):
		logger = getLogger(__name__)
		with scandir(self.path) as scan:
			for entry in scan:
				try:
					if self.on_directory is not None and is_directory(entry):
						logger.debug(f'found another directory: {entry}')
						self.on_directory(entry)
					if self.on_audio is not None and is_audio(entry):
						logger.debug(f'found an audio file: {entry}')
						self.on_audio(entry)
				except RuntimeError as x:
					logger.error(exc_info=x)
				self.progress_bar.step()

	def remove(self):
		logger = getLogger(__name__)
		self.task.cancel()
		if self.on_remove:
			self.on_remove(self)
		self.destroy()
		logger.debug(f'removed input directory: {self.path}')