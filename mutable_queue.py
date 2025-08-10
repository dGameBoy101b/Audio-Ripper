from queue import Empty, Queue
from typing import Any, Iterable

def get_nowait_all(self: Queue)->list:
	'''Gets all the items currently in the queue'''
	items = list()
	while True:
		try:
			item = self.get_nowait()
		except Empty:
			break
		items.append(item)
	return items

def put_all(self: Queue, items:Iterable, block:bool=True, timeout:float|None=None):
	'''Puts all given items in the queue'''
	for item in items:
		self.put(item, block, timeout)

def tasks_done(self: Queue, count:int):
	'''Marks the given number of tasks as done'''
	for i in range(count):
		self.task_done()
		
def clear(self: Queue):
	'''Removes every item in the queue and marks them as done'''
	tasks_done(self, len(get_nowait_all(self)))

def remove_at(self:Queue, index:int|slice):
	'''Removes items at the given index or slice and marks them as done'''
	items = get_nowait_all(self)
	count = len(items)
	del items[index]
	put_all(self, items)
	tasks_done(self, count)

def remove(self:Queue, *items:Any):
	'''Removes the first occurance of every given item and marks them as done'''
	to_remove:dict[Any, int] = dict()
	for item in items:
		if item in to_remove:
			to_remove[item] += 1
		else:
			to_remove[item] = 1
	to_enqueue = list()
	dequeued = get_nowait_all(self)
	for item in dequeued:
		if item in to_remove:
			to_remove[item] -= 1
			if to_remove[item] < 1:
				del to_remove[item]
		else:
			to_enqueue.append(item)
	put_all(self, to_enqueue if len(to_remove) < 1 else dequeued)
	tasks_done(self, len(dequeued))
	if len(to_remove) > 0:
		raise ValueError(*to_remove.keys())
