from tkinter import Misc
from typing import Iterable

def explore_descendants(root: Misc)->Iterable[Misc]:
	to_explore = [root]
	while len(to_explore) > 0:
		widget = to_explore.pop()
		to_explore.extend(widget.winfo_children())
		yield widget

def explore_leaves(root: Misc)->Iterable[Misc]:
	to_explore = [root]
	while len(to_explore) > 0:
		widget = to_explore.pop()
		children = widget.winfo_children()
		to_explore.extend(children)
		if len(children) < 1:
			yield widget