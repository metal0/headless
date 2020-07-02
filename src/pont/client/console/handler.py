import sys
import trio

from pont import log, events

log = log.get_logger(__name__)

class ConsoleHandler:
	def __init__(self, emitter, nursery: trio.Nursery):
		self.__emitter = emitter
		self.__nursery = nursery
		self.__running = False
		self.__handler_event = trio.Event()

	async def __keyboard_handler(self):
		try:
			stdin = trio.wrap_file(sys.stdin)
			self.__running = True
			async for data in stdin:
				self.__emitter.emit(events.console.data_received, data)
				log.debug(f'new data: {data}')
				if self.__handler_event.is_set():
					self.__handler_event = trio.Event()
					break

			self.__running = False

		except Exception as e:
			self.__running = False
			raise e

	async def wait(self):
		await self.__handler_event.wait()

	def reset(self):
		self.__handler_event = trio.Event()

	def start(self):
		if self.__running:
			return

		self.__nursery.start_soon(self.__keyboard_handler)

	def stop(self):
		self.__handler_event.set()
