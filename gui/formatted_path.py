from dataclasses import dataclass
from os import PathLike
from typing import Callable

@dataclass(frozen=True)
class FormattedPath(PathLike):
	format:str
	args_factory:Callable[[],tuple] = None
	kwargs_factory:Callable[[],dict] = None

	def __str__(self):
		args = ()
		if self.args_factory is not None:
			args = self.args_factory()
		kwargs = dict()
		if self.kwargs_factory is not None:
			kwargs = self.kwargs_factory()
		return self.format.format(*args, **kwargs)
	
	def __fspath__(self):
		return str(self)