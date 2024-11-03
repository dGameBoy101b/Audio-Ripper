from logging import Filter, LogRecord

class ExcludeFilter(Filter):

	def __init__(self, name=''):
		super().__init__(name)

	def filter(self, record: LogRecord)->bool:
		return not super().filter(record)
