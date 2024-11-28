from tkinter import Frame, Canvas, Event, LabelFrame
from tkinter.ttk import Scrollbar, Label, Button
from .metadata_override_item import MetadataOverrideItem

class MetadataOverridesFrame(LabelFrame):

	def __init__(self, master = None):
		super().__init__(master, text='Metadata Overrides')

		self.__items = list()

		self.key_label = Label(self, text='Key', justify='center')
		self.key_label.grid(row=0, column=0)

		self.value_label = Label(self, text='Value', justify='center')
		self.value_label.grid(row=0, column=1)

		self.add_button = Button(self, text='+', command=self.__add, width=2)
		self.add_button.grid(row=0, column=2)

		self.canvas = Canvas(self)
		self.canvas.grid(row=1, column=0, columnspan=3, sticky='NSEW')
		self.canvas.bind('<Configure>', self.__resize_content)
		self.scrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
		self.scrollbar.grid(column=3, row=1, sticky='NSE')
		self.canvas.config(yscrollcommand=self.scrollbar.set)

		self.content = Frame(self.canvas)
		self.content.bind('<Configure>', self.__config_scrollregion)
		self.content.columnconfigure(0, weight=1)
		self.content.columnconfigure(1, weight=2)
		self.content_id = self.canvas.create_window(0, 0, window=self.content, anchor='nw', width=self.canvas['width'])

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)
		self.rowconfigure(1, weight=1)

	def __resize_content(self, event: Event):
		self.canvas.itemconfig(self.content_id, width=event.width)
		self.__config_scrollregion()

	def __config_scrollregion(self, event:Event=None):
		self.canvas.configure(scrollregion=self.canvas.bbox(self.content_id))

	def __layout_items(self):
		for i in range(len(self.__items)):
			item = self.__items[i]
			row = i+1
			item.key_entry.grid(column=0, row=row, sticky='EW')
			item.value_entry.grid(column=1, row=row, sticky='EW')
			item.remove_button.grid(column=2, row=row)
		self.__config_scrollregion()

	def __add(self):
		item = MetadataOverrideItem(self.content, self.__remove)
		self.__items.append(item)
		self.__layout_items()

	def __remove(self, item:MetadataOverrideItem):
		self.__items.remove(item)
		self.__layout_items()

	def get(self):
		for item in self.__items():
			if isinstance(item, MetadataOverrideItem):
				yield item.get()
			