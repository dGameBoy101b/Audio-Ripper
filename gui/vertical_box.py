from logging import getLogger
from platform import uname
from tkinter import Canvas, Event, EventType, Misc
from tkinter.ttk import Scrollbar, Frame
from typing import Iterable

class VerticalBox(Frame):
	def __init__(self, master:Misc=None):
		super().__init__(master)
		self.__create_widgets()
		self.__add_bindings()
		self.__config_grid()
		
	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.canvas = Canvas(self)
		self.scrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
		self.canvas.config(yscrollcommand=self.scrollbar.set)
		self.content = Frame(self.canvas)
		self.content_id = self.canvas.create_window(0, 0, anchor='nw', window=self.content)
		logger.debug(f'widgets created: {self}')

	MOUSE_WHEEL_SCROLL_SYSTEMS = {'Windows', 'Darwin'}

	BUTTON_SCROLL_SYSTEMS = {'Linux'}

	def __add_bindings(self):
		logger = getLogger(__name__)
		logger.debug(f'adding bindings... {self}')
		self.canvas.bind('<Configure>', self.__resize_content)
		self.content.bind('<Configure>', self.__update_scroll_region)
		system = uname().system
		if system in VerticalBox.MOUSE_WHEEL_SCROLL_SYSTEMS:
			self.bind('<MouseWheel>', self.__forward_mouse_wheel_scroll)
		elif system == VerticalBox.BUTTON_SCROLL_SYSTEMS:
			self.bind('<Button-4>', self.__forward_button_scroll)
			self.bind('<Button-5>', self.__forward_button_scroll)
		else:
			logger.warning(f'scroll events not supported on system: {system}')
		self.bind_scroll_forwarding(self.canvas)
		self.bind_scroll_forwarding(self.content)
		logger.debug(f'bindings added: {self}')
	
	def __forward_mouse_wheel_scroll(self, event: Event):
		if event.type != EventType.MouseWheel:
			raise ValueError(f'should be mouse wheel event: {event.type}')
		self.scrollbar.event_generate('<MouseWheel>', delta=event.delta)

	def __forward_button_scroll(self, event: Event):
		if event.type != EventType.Button:
			raise ValueError(f'should be button event: {event.type}')
		if event.num not in {4, 5}:
			raise ValueError(f'should be button 4 or button 5 event: button {event.num}')
		self.scrollbar.event_generate(f'<Button-{event.num}', delta=event.delta)

	def bind_scroll_forwarding(self, widget: Misc):
		tags = list(widget.bindtags())
		tags.append(str(self))
		widget.bindtags(tags)
	
	def unbind_scroll_forwarding(self, widget: Misc):
		tags = list(widget.bindtags())
		tags.remove(str(self))
		widget.bindtags(tags)	

	def __config_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.canvas.columnconfigure(0, weight=1)
		self.canvas.grid(row=0, column=0, sticky='NSEW')
		self.scrollbar.grid(row=0, column=1, sticky='NSE')
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		logger.debug(f'grid configured: {self}')

	def __resize_content(self, event: Event):
		if event.type != EventType.Configure:
			raise ValueError(f'should be configure event to resize content: {event.type}')
		self.canvas.itemconfig(self.content_id, width=event.width)

	def __update_scroll_region(self, event:Event):
		if event.type != EventType.Configure:
			raise ValueError(f'should be configure event to update scroll region: {event.type}')
		self.canvas.config(scrollregion=self.canvas.bbox(self.content_id))