from tkinter import Event, LabelFrame
from tkinter.ttk import Button, Label
from .vertical_box import VerticalBox
from .metadata_override_item import MetadataOverrideItem

class MetadataOverridesFrame(LabelFrame):

	def __init__(self, master = None):
		super().__init__(master, text='Metadata Overrides')

		self.__items:list[MetadataOverrideItem] = list()
		self.__destroy_bindings = dict()

		self.content_box = VerticalBox(self)
		self.key_label = Label(self.content_box, text='Key', justify='center')
		self.value_label = Label(self.content_box, text='Value', justify='center')
		self.add_button = Button(self.content_box, text='+', command=self.add, width=2)

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

	def __layout_items(self):
		for row in range(len(self.__items)):
			item = self.__items[row]
			print(f'layed out item in row {row}: {item}')
			item.grid(column=0, row=row, sticky='EW', columnspan=3)
		print(f'layed out {len(self.__items)} metadata overrides')
		self.update()

	def __item_destroyed(self, event: Event):
		self.remove(event.widget)

	def add(self, key:str='', value:str=''):
		item = MetadataOverrideItem(self.content_box.content, key, value)
		binding = item.bind('<Destroy>', self.__item_destroyed)
		self.__destroy_bindings[item] = binding
		self.__items.append(item)
		self.__layout_items()

	def remove(self, item:MetadataOverrideItem):
		print(f'removed {item} at index {self.__items.index(item)}')
		self.__items.remove(item)
		item.unbind('<Destroy>', self.__destroy_bindings[item])
		del self.__destroy_bindings[item]
		self.__layout_items()

	def get(self)->dict[str, str]:
		result = dict()
		for item in self.__items():
			if isinstance(item, MetadataOverrideItem):
				pair = item.get()
				result[pair[0]] = pair[1]
		return result
	
	def destroy(self):
		for item in self.__items:
			item.unbind('<Destroy>', self.__destroy_bindings[item])
		self.__destroy_bindings.clear()
		self.__items.clear()
		return super().destroy()
			