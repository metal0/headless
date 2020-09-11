import inspect
import time

from loguru import logger

from pont.client import events
from pont.world.net import SMSG_AUTH_RESPONSE, SMSG_PONG, SMSG_WARDEN_DATA
from . import packets
from .opcode import Opcode
from .packets.auth_packets import AuthResponse
from ..errors import ProtocolError


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
			Opcode.SMSG_NAME_QUERY_RESPONSE: self.handle_name_query_response,
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
				logger.log('PACKETS', f'Dropped packet: {packet.header}')
				return

			if inspect.iscoroutinefunction(fn):
				# noinspection PyUnresolvedReferences, PyArgumentList
				return await fn(packet)
			else:
				# noinspection PyArgumentList
				return fn(packet)

		except KeyError:
			logger.log('PACKETS', f'Dropped packet: {packet.header}')
			return

	async def handle_name_query_response(self, packet: packets.SMSG_NAME_QUERY_RESPONSE):
		self._emitter.emit(events.world.received_name_query_response)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_duel_requested(self, packet: packets.SMSG_DUEL_REQUESTED):
		self._emitter.emit(events.world.received_duel_request)
		logger.log('PACKETS', f'packet={packet}')
		await self._world.protocol.send_CMSG_DUEL_ACCEPTED()

	async def handle_gm_chat_message(self, packet: packets.SMSG_GM_MESSAGECHAT):
		self._emitter.emit(events.world.received_gm_chat_message)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_chat_message(self, packet: packets.SMSG_MESSAGECHAT):
		self._emitter.emit(events.world.received_chat_message)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_guild_invite(self, packet: packets.SMSG_GROUP_INVITE):
		self._emitter.emit(events.world.received_guild_invite)
		logger.log('PACKETS', f'packet={packet}')
		await self._world.protocol.send_CMSG_GUILD_ACCEPT()

	async def handle_group_invite(self, packet: packets.SMSG_GROUP_INVITE):
		self._emitter.emit(events.world.received_group_invite)
		logger.log('PACKETS', f'packet={packet}')
		await self._world.protocol.send_CMSG_GROUP_ACCEPT()

	async def handle_logout_complete(self, packet: packets.SMSG_LOGOUT_COMPLETE):
		self._emitter.emit(events.world.logged_out)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_logout_response(self, packet: packets.SMSG_LOGOUT_RESPONSE):
		self._emitter.emit(events.world.received_logout_response, reason=packet.reason, instant_logout=packet.instant_logout)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_logout_cancel_ack(self, packet: packets.SMSG_LOGOUT_CANCEL_ACK):
		self._emitter.emit(events.world.logout_cancelled)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_time_sync_request(self, packet: packets.SMSG_TIME_SYNC_REQ):
		self._emitter.emit(events.world.received_time_sync_request, id=packet.id)
		logger.log('PACKETS', f'packet={packet}')

		# TODO: Defer this to something like n.start_soon(client.anti_afk) instead of (await client.anti_afk() or
		#  await client.start_anti_afk()) where inside we will write
		#  packet = await self.world.protocol.wait_for_packet(Opcode.SMSG_TIME_SYNC_REQ)
		await self._world.protocol.send_CMSG_TIME_SYNC_RES(
			id=packet.id,
			client_ticks=int(1000 * time.time())
		)

		self._time_sync_count += 1

	def handle_tutorial_flags(self, packet: packets.SMSG_TUTORIAL_FLAGS):
		self._emitter.emit(events.world.received_tutorial_flags, packet=packet)
		logger.log('PACKETS', f'packet={packet}')

	def handle_auth_response(self, packet: SMSG_AUTH_RESPONSE):
		self._emitter.emit(events.world.received_auth_response, packet=packet)
		logger.log('PACKETS', f'packet={packet}')
		if packet.response == AuthResponse.ok:
			self._emitter.emit(events.world.logged_in)

		elif packet.response == AuthResponse.wait_queue:
			self._emitter.emit(events.world.in_queue, packet.queue_position)

		else:
			raise ProtocolError(str(packet.response))

	def handle_char_enum(self, packet: packets.SMSG_CHAR_ENUM):
		self._emitter.emit(events.world.received_char_enum, characters=packet.characters)
		logger.log('PACKETS', f'packet={packet}')

	def handle_login_verify_world(self, packet: packets.SMSG_LOGIN_VERIFY_WORLD):
		self._emitter.emit(events.world.received_login_world, packet=packet)
		self._emitter.emit(events.world.entered_world)
		logger.log('PACKETS', f'packet={packet}')

	def handle_warden_data(self, packet: SMSG_WARDEN_DATA):
		self._emitter.emit(events.world.received_warden_data, packet=packet)
		logger.log('PACKETS', f'packet={packet}')

	def handle_pong(self, packet: SMSG_PONG):
		self._emitter.emit(events.world.received_pong, packet=packet)
		logger.log('PACKETS', f'packet={packet}')
