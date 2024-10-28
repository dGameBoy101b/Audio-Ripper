from tkinter import ttk
import tkinter
from metadata_override_item import MetadataOverrideItem

class MetadataOverridesFrame(ttk.LabelFrame):

	def __init__(self, master = None):
		super().__init__(master, text='Metadata Overrides')
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)
		self.rowconfigure(1, weight=1)

		self.key_label = ttk.Label(self, text='Key', justify='center')
		self.key_label.grid(row=0, column=0, sticky='EW')

		self.value_label = ttk.Label(self, text='Value', justify='center')
		self.value_label.grid(row=0, column=1, sticky='EW')

		self.add_button = ttk.Button(self, text='+', command=self.__add, width=2)
		self.add_button.grid(row=0, column=2)

		self.__items = list()

	def __layout_items(self):
		for i in range(len(self.__items)):
			item = self.__items[i]
			row = i+1
			item.key_entry.grid(column=0, row=row, sticky='EW')
			item.value_entry.grid(column=1, row=row, sticky='EW')
			item.remove_button.grid(column=2, row=row)

	def __add(self):
		item = MetadataOverrideItem(self, self.__remove)
		self.__items.append(item)
		row = len(self.__items)
		print(f'added at row: {row}')
		self.__layout_items()

	def __remove(self, item:MetadataOverrideItem):
		self.__items.remove(item)
		print(f'removed item: {len(self.__items)}')
		self.__layout_items()

	def get(self):
		for item in self.__items():
			if isinstance(item, MetadataOverrideItem):
				yield item.get()
			