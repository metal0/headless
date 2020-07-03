import inspect
import time

from pont.client.world.net.packets import SMSG_AUTH_RESPONSE, SMSG_PONG, SMSG_WARDEN_DATA
from pont.client.world.net.packets.constants import Opcode
from . import packets
from .packets.auth_packets import AuthResponse
from ..errors import ProtocolError
from ... import events, log

log = log.mgr.get_logger(__name__)

class WorldHandler:
	def __init__(self, emitter, world):
		self._emitter = emitter
		self._packet_map = {
			Opcode.SMSG_AUTH_RESPONSE: self.handle_auth_response,
			Opcode.SMSG_WARDEN_DATA: self.handle_warden_data,
			Opcode.SMSG_PONG: self.handle_pong,
			Opcode.SMSG_CHAR_ENUM: self.handle_char_enum,
			Opcode.SMSG_LOGIN_VERIFY_WORLD: self.handle_login_verify_world,
			Opcode.SMSG_TUTORIAL_FLAGS: self.handle_tutorial_flags,
			Opcode.SMSG_TIME_SYNC_REQ: self.handle_time_sync_request,
		}

		self._world = world
		self._time_sync_count = 0
		self._handler_start_time = time.time()

	async def handle(self, packet):
		try:
			# log.debug(f'handle {packet}')
			fn = self._packet_map[packet.header.opcode]

			if fn is None:
				log.debug(f'Dropped packet: {packet.header}')
				return

			if inspect.iscoroutinefunction(fn):
				# noinspection PyUnresolvedReferences, PyArgumentList
				return await fn(packet)
			else:
				# noinspection PyArgumentList
				return fn(packet)

		except KeyError:
			log.debug(f'Dropped packet: {packet.header}')
			return

	async def handle_time_sync_request(self, packet: packets.SMSG_TIME_SYNC_REQ):
		self._emitter.emit(events.world.received_SMSG_TIME_SYNC_REQ, id=packet.id)
		log.debug(f'[handle_time_sync_request] packet={packet}')

		# TODO: Defer this to something like n.start_soon(client.anti_afk) instead of (await client.anti_afk() or
		#  await client.start_anti_afk()) where inside we will write
		#  packet = await self.world.protocol.wait_for_packet(Opcode.SMSG_TIME_SYNC_REQ)
		await self._world.protocol.send_CMSG_TIME_SYNC_RES(
			id=self._time_sync_count,
			client_ticks=int(1000 * (time.time() - self._handler_start_time))
		)

		self._time_sync_count += 1

	def handle_tutorial_flags(self, packet: packets.SMSG_TUTORIAL_FLAGS):
		self._emitter.emit(events.world.received_SMSG_TUTORIAL_FLAGS, packet=packet)
		log.debug(f'[handle_tutorial_flags] packet={packet}')

	def handle_auth_response(self, packet: SMSG_AUTH_RESPONSE):
		self._emitter.emit(events.world.received_SMSG_AUTH_RESPONSE, packet=packet)
		log.debug(f'[handle_auth_response] packet={packet}')
		if packet.response == AuthResponse.ok:
			self._emitter.emit(events.world.logged_in)

		elif packet.response == AuthResponse.wait_queue:
			self._emitter.emit(events.world.in_queue, packet.queue_position)

		else:
			raise ProtocolError(str(packet.response))

	def handle_char_enum(self, packet: packets.SMSG_CHAR_ENUM):
		self._emitter.emit(events.world.received_SMSG_CHAR_ENUM, characters=packet.characters)
		log.debug(f'[handle_char_enum] packet={packet}')

	def handle_login_verify_world(self, packet: packets.SMSG_LOGIN_VERIFY_WORLD):
		self._emitter.emit(events.world.received_SMSG_LOGIN_VERIFY_WORLD, packet=packet)
		self._emitter.emit(events.world.ingame)
		log.debug(f'[handle_login_verify_world] packet={packet}')

	def handle_warden_data(self, packet: SMSG_WARDEN_DATA):
		self._emitter.emit(events.world.received_SMSG_WARDEN_DATA, packet=packet)
		log.debug(f'[handle_warden_data] packet={packet}')

	def handle_pong(self, packet: SMSG_PONG):
		self._emitter.emit(events.world.received_SMSG_PONG, packet=packet)
		log.debug(f'[handle_pong] packet={packet}')
