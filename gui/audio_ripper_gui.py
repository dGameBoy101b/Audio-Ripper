from tkinter import ttk
from .settings_frame import SettingsFrame
from .input_frame import InputFrame
from .output_frame import OutputFrame

class AudioRipperGUI(ttk.Frame):

	def __init__(self, master=None):
		ttk.Frame.__init__(self, master)
		self.grid(sticky='NSEW')
		self.rowconfigure(0, weight=1)
		self.columnconfigure([0,1,2], weight=1)
		self._create_child_widgets()

	def _create_child_widgets(self):
		self.settingsFrame = SettingsFrame(self)
		self.settingsFrame.grid(column=0, row=0, sticky='NSEW')
		self.inputFrame = InputFrame(self)
		self.inputFrame.grid(column=1, row=0, sticky='NSEW')
		self.outputFrame = OutputFrame(self)
		self.outputFrame.grid(column=2, row=0, sticky='NSEW')

	def configure_window(self):
		window = self.winfo_toplevel()
		window.title('Audio Ripper')
		window.columnconfigure(0, weight=1)
		window.rowconfigure(0, weight=1)

def main():
	app = AudioRipperGUI()
	app.configure_window()
	app.mainloop()

if __name__ == '__main__':
	main()