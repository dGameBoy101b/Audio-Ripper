from os import PathLike, scandir, listdir
from tkinter import ttk
from asyncio import create_task
from typing import Callable
from ..scan_for_audio import is_audio, is_directory

class InputDirectoryItem(ttk.Frame):

	def __init__(self, path:PathLike, on_remove:Callable[['InputDirectoryItem'],None]=None, on_audio:Callable[[PathLike],None]=None, on_directory:Callable[[PathLike],None]=None, master:ttk.Widget=None, **kwargs):
		super().__init__(master, **kwargs)

		self.path = path
		self.on_remove = on_remove
		self.on_audio = on_audio
		self.on_directory = on_directory

		self.text = ttk.Label(self, text=str(path))
		self.remove_button = ttk.Button(self, text='x', command=self.remove)
		self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', maximum=len(listdir(path)))

		self.text.grid(column=0, row=0, sticky='EW')
		self.remove_button.grid(column=1, row=0)
		self.progress_bar.grid(column=0, columnspan=1, row=1, sticky='EW')
		self.columnconfigure(0, weight=1)
		
		self.task = create_task(self.__scan())

	async def __scan(self):
		with scandir(self.path) as scan:
			for entry in scan:
				try:
					if self.on_directory is not None and is_directory(entry):
						self.on_directory(entry)
					if self.on_audio is not None and is_audio(entry):
						self.on_audio(entry)
				except RuntimeError as x:
					print(x)
				self.progress_bar.step()

	def remove(self):
		self.task.cancel()
		if self.on_remove:
			self.on_remove(self)
		self.destroy()
		print(f'removed input directory: {self.path}')