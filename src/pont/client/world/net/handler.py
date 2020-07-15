import inspect
import time

from pont.client.world.net.packets import SMSG_AUTH_RESPONSE, SMSG_PONG, SMSG_WARDEN_DATA
from .opcode import Opcode
from . import packets
from .packets.auth_packets import AuthResponse
from ..errors import ProtocolError
from ... import events
from loguru import logger

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
			Opcode.SMSG_LOGOUT_RESPONSE: self.handle_logout_response,
			Opcode.SMSG_LOGOUT_CANCEL_ACK: self.handle_logout_cancel_ack,
			Opcode.SMSG_LOGOUT_COMPLETE: self.handle_logout_complete,
			Opcode.SMSG_GROUP_INVITE: self.handle_group_invite,
			Opcode.SMSG_GUILD_INVITE: self.handle_guild_invite,
			Opcode.SMSG_GM_MESSAGECHAT: self.handle_gm_chat_message,
			Opcode.SMSG_MESSAGECHAT: self.handle_chat_message,
			Opcode.SMSG_DUEL_REQUESTED: self.handle_duel_requested,
		}

		self._world = world
		self._time_sync_count = 0
		self._handler_start_time = time.time()

	async def handle(self, packet):
		try:
			fn = self._packet_map[packet.header.opcode]

			if fn is None:
				logger.debug(f'Dropped packet: {packet.header}')
				return

			if inspect.iscoroutinefunction(fn):
				# noinspection PyUnresolvedReferences, PyArgumentList
				return await fn(packet)
			else:
				# noinspection PyArgumentList
				return fn(packet)

		except KeyError:
			logger.debug(f'Dropped packet: {packet.header}')
			return

	async def handle_duel_requested(self, packet: packets.SMSG_DUEL_REQUESTED):
		self._emitter.emit(events.world.received_duel_request)
		logger.debug(f'packet={packet}')
		await self._world.protocol.send_CMSG_DUEL_ACCEPTED()

	async def handle_gm_chat_message(self, packet: packets.SMSG_GM_MESSAGECHAT):
		self._emitter.emit(events.world.received_gm_chat_message)
		logger.debug(f'packet={packet}')

	async def handle_chat_message(self, packet: packets.SMSG_MESSAGECHAT):
		self._emitter.emit(events.world.received_chat_message)
		logger.debug(f'packet={packet}')

	async def handle_guild_invite(self, packet: packets.SMSG_GROUP_INVITE):
		self._emitter.emit(events.world.received_guild_invite)
		logger.debug(f'packet={packet}')
		await self._world.protocol.send_CMSG_GUILD_ACCEPT()

	async def handle_group_invite(self, packet: packets.SMSG_GROUP_INVITE):
		self._emitter.emit(events.world.received_group_invite)
		logger.debug(f'packet={packet}')
		await self._world.protocol.send_CMSG_GROUP_ACCEPT()

	async def handle_logout_complete(self, packet: packets.SMSG_LOGOUT_COMPLETE):
		self._emitter.emit(events.world.logged_out)
		logger.debug(f'packet={packet}')

	async def handle_logout_response(self, packet: packets.SMSG_LOGOUT_RESPONSE):
		self._emitter.emit(events.world.received_SMSG_LOGOUT_RESPONSE, reason=packet.reason, instant_logout=packet.instant_logout)
		logger.debug(f'packet={packet}')

	async def handle_logout_cancel_ack(self, packet: packets.SMSG_LOGOUT_CANCEL_ACK):
		self._emitter.emit(events.world.logout_cancelled)
		logger.debug(f'packet={packet}')

	async def handle_time_sync_request(self, packet: packets.SMSG_TIME_SYNC_REQ):
		self._emitter.emit(events.world.received_SMSG_TIME_SYNC_REQ, id=packet.id)
		logger.debug(f'packet={packet}')

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
		logger.debug(f'packet={packet}')

	def handle_auth_response(self, packet: SMSG_AUTH_RESPONSE):
		self._emitter.emit(events.world.received_SMSG_AUTH_RESPONSE, packet=packet)
		logger.debug(f'packet={packet}')
		if packet.response == AuthResponse.ok:
			self._emitter.emit(events.world.logged_in)

		elif packet.response == AuthResponse.wait_queue:
			self._emitter.emit(events.world.in_queue, packet.queue_position)

		else:
			raise ProtocolError(str(packet.response))

	def handle_char_enum(self, packet: packets.SMSG_CHAR_ENUM):
		self._emitter.emit(events.world.received_SMSG_CHAR_ENUM, characters=packet.characters)
		logger.debug(f'packet={packet}')

	def handle_login_verify_world(self, packet: packets.SMSG_LOGIN_VERIFY_WORLD):
		self._emitter.emit(events.world.received_SMSG_LOGIN_VERIFY_WORLD, packet=packet)
		self._emitter.emit(events.world.ingame)
		logger.debug(f'packet={packet}')

	def handle_warden_data(self, packet: SMSG_WARDEN_DATA):
		self._emitter.emit(events.world.received_SMSG_WARDEN_DATA, packet=packet)
		logger.debug(f'packet={packet}')

	def handle_pong(self, packet: SMSG_PONG):
		self._emitter.emit(events.world.received_SMSG_PONG, packet=packet)
		logger.debug(f'packet={packet}')
