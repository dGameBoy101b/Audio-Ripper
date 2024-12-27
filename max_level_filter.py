from logging import Filter, LogRecord

class MaxLevelFilter:
	def __init__(self, level:int):
		self.level = level

	def filter(self, log:LogRecord)->bool:
		return log.levelno <= self.level