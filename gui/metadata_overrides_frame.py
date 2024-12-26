from logging import getLogger
from tkinter import Event, LabelFrame
from tkinter.ttk import Button, Label

from .widget_exploration import explore_descendants
from .vertical_box import VerticalBox
from .metadata_override_item import MetadataOverrideItem

class MetadataOverridesFrame(LabelFrame):

	def __init__(self, master = None):
		super().__init__(master, text='Metadata Overrides')
		self.__destroy_bindings = dict()
		self.__create_widgets()
		self.__configure_grid()

	def __create_widgets(self):
		logger = getLogger(__name__)
		logger.debug(f'creating widgets... {self}')
		self.content_box = VerticalBox(self)
		self.key_label = Label(self.content_box, text='Key', anchor='center')
		self.value_label = Label(self.content_box, text='Value', anchor='center')
		self.add_button = Button(self.content_box, text='+', command=self.add, width=2)
		logger.debug(f'widgets created: {self}')

	def __configure_grid(self):
		logger = getLogger(__name__)
		logger.debug(f'configuring grid... {self}')
		self.key_label.grid(row=0, column=0, sticky='EW')
		self.value_label.grid(row=0, column=1, sticky='EW')
		self.add_button.grid(row=0, column=2)
		self.content_box.canvas.grid_configure(row=1, column=0, columnspan=3)
		self.content_box.scrollbar.grid_configure(row=1, column=3)

		self.content_box.grid(row=0, column=0, sticky='NSEW')
		self.content_box.columnconfigure(0, weight=1)
		self.content_box.columnconfigure(1, weight=2)
		self.content_box.rowconfigure(0, weight=0)
		self.content_box.rowconfigure(1, weight=1)
		self.content_box.content.columnconfigure(0, weight=1)
		self.content_box.content.columnconfigure(1, weight=2)

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		logger.debug(f'grid configured: {self}')

	def __layout_items(self):
		logger = getLogger(__name__)
		row = 0
		for item in self.content_box.content.winfo_children():
			if not item.winfo_exists():
				continue
			item.grid(column=0, row=row, sticky='EW', columnspan=3)
			row += 1
		logger.info(f'layed out {len(self.__items)} metadata overrides')
		self.update()

	def __item_destroyed(self, event: Event):
		item:MetadataOverrideItem = event.widget
		print(f'removed metadata override: {item}')
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		self.__layout_items()

	def add(self, key:str='', value:str=''):
		item = MetadataOverrideItem(self.content_box.content, key, value)
		binding = item.bind('<Destroy>', self.__item_destroyed)
		self.__destroy_bindings[item] = binding
		for widget in explore_descendants(item):
			self.content_box.bind_scroll_forwarding(widget)
		self.__layout_items()

	def remove(self, key:str):
		logger = getLogger(__name__)
		missing = True
		for item in self.content_box.content.winfo_children():
			if item.winfo_exists() and isinstance(item, MetadataOverrideItem) and item.get_key() == key:
				logger.info(f'removed metadata override: {item}')
				item.destroy()
				missing = False
		if missing:
			raise KeyError(key)

	def get(self)->dict[str, str]:
		result = dict()
		for item in self.content_box.content.winfo_children():
			if item.winfo_exists() and isinstance(item, MetadataOverrideItem):
				result[item.get_key()] = item.get_value()
		return result
	
	def destroy(self):
		for item in self.content_box.content.winfo_children():
			item.unbind('<Destroy>', self.__destroy_bindings[item])
		self.__destroy_bindings.clear()
		return super().destroy()
			