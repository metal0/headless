import trio

from pont_client.client import events, auth, log
log = log.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._receiver_started = trio.Event()

	async def _receiver(self, emitter):
		self._receiver_started.set()
		emitter.emit(events.world.connected, stream=self.stream)
		log.debug('receiver started')

		try:
			while True:
				data = await self.stream.receive_some()
				log.debug(f'received: {data=}')
				if not data:
					await self.stream.send_eof()
					emitter.emit(events.world.disconnected, reason=f'EOF received')
					break
				emitter.emit(events.world.data_received, data=data)

		except Exception as e:
			emitter.emit(events.world.disconnected, reason=f'{e}')
			log.error(f'_receiver error: {e}')

	async def spawn_receiver(self, stream, nursery, emitter):
		receiver_started = trio.Event()
		nursery.start_soon(self._receiver, emitter)
		await receiver_started.wait()
		self.stream = stream

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
		self._receiver_started = trio.Event()
