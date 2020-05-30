import trio
from pont import events, log

log = log.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.SocketStream, emitter):
		self.stream = stream
		self.__emitter = emitter

async def receiver(receiver_started: trio.Event, stream: trio.SocketStream, emitter):
	receiver_started.set()
	emitter.emit(events.world.connected, stream=stream)
	log.debug('receiver started')

	try:
		while True:
			data = await stream.receive_some()
			log.debug(f'received: {data=}')
			if not data:
				await stream.send_eof()
				emitter.emit(events.world.disconnected, reason=f'EOF received')
				break

			emitter.emit(events.world.data_received, data=data)

	except Exception as e:
		emitter.emit(events.world.disconnected, reason=f'{e}')
		log.error(f'Error: {e}')
		# raise e

async def connect(host: str, port: int, nursery: trio.Nursery, emitter) -> WorldProtocol:
	receiver_started = trio.Event()
	stream = await trio.open_tcp_stream(host=host, port=port)
	nursery.start_soon(receiver, receiver_started, stream, emitter)
	await receiver_started.wait()
	return WorldProtocol(stream=stream, emitter=emitter)
