from queue import Empty, Queue
from typing import Any

class MutableQueue(Queue):

	def get_nowait_all(self)->list:
		'''Gets all the items currently in the queue'''
		items = list()
		while True:
			try:
				item = self.get_nowait()
			except Empty:
				break
			items.append(item)
		return items
	
	def put_all(self, items:list, block:bool=True, timeout:float|None=None):
		'''Puts all given items in the queue'''
		for item in items:
			self.put(item, block, timeout)

	def tasks_done(self, count:int):
		'''Marks the given number of tasks as done'''
		for i in range(count):
			self.task_done()
	
	def clear(self):
		'''Removes every item in the queue and marks them as done'''
		self.tasks_done(len(self.get_nowait_all()))
	
	def remove_at(self, index:int|slice):
		'''Removes items at the given index or slice and marks them as done'''
		items = self.get_nowait_all()
		count = len(items)
		del items[index]
		self.put_nowait_all(items)
		self.tasks_done(count)

	def remove(self, *items):
		'''Removes the first occurance of every given item and marks them as done'''
		to_remove:dict[Any, int] = dict()
		for item in items:
			if item in to_remove:
				to_remove[item] += 1
			else:
				to_remove[item] = 1
		to_enqueue = list()
		dequeued = self.get_nowait_all()
		for item in dequeued:
			if item in to_remove:
				to_remove[item] -= 1
				if to_remove[item] < 1:
					del to_remove[item]
			else:
				to_enqueue.append(item)
		self.put_nowait_all(to_enqueue if len(to_remove) < 1 else dequeued)
		self.tasks_done(len(dequeued))
		if len(to_remove) > 0:
			raise ValueError(*to_remove.keys())
		