from tkinter import Canvas, Event, Misc
from tkinter.ttk import Scrollbar, Frame

class VerticalBox(Frame):
	def __init__(self, master:Misc=None):
		super().__init__(master)

		self.canvas = Canvas(self)
		self.scrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
		self.canvas.config(yscrollcommand=self.scrollbar.set)
		self.canvas.bind('<Configure>', self.__resize_content)
		self.content = Frame(self.canvas)
		self.bind('<Configure>', self.update_scrollregion)
		self.content_id = self.canvas.create_window(0, 0, anchor='nw', window=self.content)
		
		self.canvas.columnconfigure(0, weight=1)
		self.canvas.grid(row=0, column=0, sticky='NSEW')
		self.scrollbar.grid(row=0, column=1, sticky='NSE')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
	def __resize_content(self, event: Event):
		self.canvas.itemconfig(self.content_id, width=event.width)

	def update_scrollregion(self, event:Event=None):
		self.canvas.config(scrollregion=self.canvas.bbox(self.content_id))