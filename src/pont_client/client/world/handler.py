import trio

from pont import events, log, utility
from pont.client import world
from typing import Optional

from pont.utility.scoped_emitter import ScopedEmitter
from pont.client.world import SMSG_CHAR_ENUM

log = log.get_logger(__name__)

_opcode_event_map = {
	world.opcodes.SMSG_AUTH_CHALLENGE: events.world.received_auth_challenge,
    world.opcodes.SMSG_AUTH_RESPONSE: events.world.received_auth_response,
	world.opcodes.SMSG_NAME_QUERY_RESPONSE: events.world.received_name_query_response
}

class WorldHandler(ScopedEmitter):
	def __init__(self, context):
		super().__init__(context.emitter)
		self.__context = context
		self.__stream: Optional[trio.SocketStream] = None
		self.__stream_event = trio.Event()

	async def __ensure_stream_integriy(self):
		with trio.fail_after(5):
			while True:
				await trio.hazmat.checkpoint()
				if self.__stream_event.is_set():
					break

	def install(self):
		@self.on(events.world.connected)
		def on_connected(stream):
			log.debug(f'stream obtained: {stream}')
			self.__stream = stream
			self.__stream_event.set()

		@self.on(events.world.data_received)
		async def handle_packet(data: bytes):
			await self.__ensure_stream_integriy()
			opcode = pont.client.world.dispatch.parse_opcode(data=data)
			if opcode in _opcode_event_map:
				packet = None
				error_data = None
				try:
					await trio.hazmat.checkpoint()
					packet = pont.client.world.dispatch.parse(packet=data)
					log.debug(f'packet received: {opcode} {data}')

				except (utility.StructParseError, pont.client.world.dispatch.InvalidPacket) as e:
					log.debug(f'Packet data: {data}')
					await trio.hazmat.checkpoint()

				self.emit(_opcode_event_map[opcode], packet=packet, error_data=error_data)

			else:
				log.debug(f'Packet dropped: {opcode}: {data}')

		@self.on(events.world.received_char_enum)
		async def handle_char_enum(packet: SMSG_CHAR_ENUM):
			pass

		@self.on(events.world.received_auth_challenge)
		async def handle_auth_challenge():
			pass