from tkinter import Tk
from asyncio import sleep, new_event_loop
from logging import getLogger

class AsyncTk(Tk):

	def __init__(self, sleep:float=.05):
		logger = getLogger(__name__)

		Tk.__init__(self, className='AsyncTk')
		logger.debug('created tk')

		self.sleep = sleep
		self.task = None
		self.loop = new_event_loop()
		self.task = self.loop.create_task(self.__update_gui())
		logger.debug('created event loop')

	async def __update_gui(self):
		while True:
			self.update()
			await sleep(self.sleep)

	def mainloop(self, n = 0):
		logger = getLogger(__name__)
		logger.info('main loop run forever')
		self.loop.run_forever()

	def destroy(self):
		logger = getLogger(__name__)
		super().destroy()
		self.loop.stop()
		logger.info('main loop stopped')
