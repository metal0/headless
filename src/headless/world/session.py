import datetime
import time
import uuid
from pathlib import Path

import trio
import random

# import esper as esper
from contextlib import asynccontextmanager
from typing import Optional, Tuple, Any, List
from loguru import logger
from trio_socks import socks5
from wlink.auth.realm import Realm
from wlink.cryptography import sha
from wlink.utility.construct import int32
from wlink.world import WorldClientStream
from wlink.world.errors import ProtocolError
from wlink.world.packets import AuthResponse, CharacterInfo, Opcode, SMSG_AUTH_CHALLENGE, make_CMSG_AUTH_SESSION, \
	make_CMSG_CHAR_ENUM, make_CMSG_PLAYER_LOGIN, make_CMSG_LOGOUT_REQUEST, CMSG_LOGOUT_REQUEST, CMSG_PLAYER_LOGIN, \
	CMSG_CHAR_ENUM, CMSG_AUTH_SESSION, make_CMSG_PING, CMSG_PING, make_CMSG_TIME_SYNC_RESP, CMSG_TIME_SYNC_RESP, \
	CMSG_KEEP_ALIVE, make_CMSG_KEEP_ALIVE

from .character import Character
from .chat import ChatMessage, LocalChat
from .warden import Warden
from .. import world, events
from .handler import WorldHandler
from .names import NameCache
from .player import LocalPlayer
from .state import WorldState
from ..utility.emitter import BaseEmitter, wait_for_event
from ..utility.history import History

MAX_PACKET_QUEUE = 100

class SessionCrypto:
	def __init__(self, session_key, server_seed, encryption_seed1, encryption_seed2):
		self.session_key = session_key
		self.server_seed = server_seed
		self.encryption_seed1 = encryption_seed1
		self.encryption_seed2 = encryption_seed2
		self.client_seed = random.getrandbits(32)

	def account_hash(self, username: str):
		return sha.sha1(
			username, bytes([0] * 4),
			self.client_seed,
			self.server_seed,
			self.session_key, out=int
		)

class WorldSession:
	def __init__(self, nursery: trio.Nursery, emitter=None, proxy: Optional[Tuple[str, int]] = None):
		self.proxy = proxy
		if emitter is None:
			emitter = BaseEmitter(emitter=emitter)

		self.emitter = emitter
		self.handler = WorldHandler(world=self)

		self.warden: Optional[Warden] = None
		self.nursery: Optional[trio.Nursery] = None
		self.local_player: Optional[LocalPlayer] = None
		self.chat: Optional[LocalChat] = None
		self.stream: Optional[WorldClientStream] = None
		self.history = History()

		# self.packets: Optional[trio.MemoryReceiveChannel] = None
		# self._store_packet: Optional[trio.MemorySendChannel] = None

		self._state = WorldState.not_connected
		self._parent_nursery = nursery
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._crypto: Optional[SessionCrypto] = None
		self._realm = None
		self._username = None
		self._handling_packets = False
		self.names = NameCache(self)

	@property
	def state(self):
		return self._state

	@property
	def realm(self) -> Realm:
		return self._realm

	@property
	def session_key(self):
		return self._crypto.session_key

	async def aclose(self):
		if self._stream is not None:
			await self._stream.send_eof()
			await self._stream.aclose()

		self._handling_packets = False
		self._state = WorldState.not_connected

	# Wait for the given event under an optional condition to occur (once) and return a transform of the event keyword
	# arguments.
	async def wait_for_event(self, event, condition=None, result_transform=None) -> Any:
		return await wait_for_event(self.emitter, event=event, condition=condition, result_transform=result_transform)

	async def wait_for_message(self) -> ChatMessage:
		return await wait_for_event(self.emitter, event=events.world.received_chat_message, condition=None, result_transform=lambda *args, **kwargs: kwargs['message'])

	# Wait for a packet to be received under a certain condition and return it.
	async def wait_packet_condition(self, condition):
		if not self._handling_packets:
			raise ProtocolError('Packet handler stopped')

		def condition_mod(packet, **kwargs):
			return condition(packet)

		def transform(packet, **kwargs):
			return packet

		return await self.wait_for_event(
			events.world.received_packet,
			condition=condition_mod,
			result_transform=transform
		)

	# TODO: Maybe make this some sort of asynccontextmanager so that waiting for a packet is more
	#   time independent. A (rare, maybe impossible?) scenario in which a packet could arrive without this
	#   function noticing is that a packet arrives in between sending a request and waiting for a response.
	#   However, I believe it might be the case that due to the nature of the event loop, as long as no async
	#   functions are awaited in between, then wait_for_packet will definitely see the packet that arrived before
	#   I/O was polled. The context manager idea might still be valid for those cases where we have to await some
	#   async function in between sending and receiving the packet.
	#   ?????
	# Wait for a packet to be received and return it.
	async def wait_for_packet(self, opcode: Opcode) -> Any:
		def _condition(packet):
			if packet is None:
				return False
			
			return packet.header.opcode == opcode

		return await self.wait_packet_condition(_condition)

	# Wait for a packet to be received and return it.
	async def wait_for_any_packet(self, *opcodes: List[Opcode]) -> Any:
		return await self.wait_packet_condition(lambda packet: packet.header.opcode in opcodes)

	@staticmethod
	def _default_condition(**kwargs):
		return True

	async def _packet_handler(self, *, task_status=trio.TASK_STATUS_IGNORED):
		task_status.started()
		logger.log('PACKETS', 'started')
		try:
			self._handling_packets = True
			# TODO: Some sort of packet queue to allow for late wait_for_packet usage
			async for packet in self.stream.decrypted_packets():
				self.history.add(packet)
				await self.handler.handle(packet)

		except trio.Cancelled:
			raise

		except KeyboardInterrupt as e:
			raise e

		except world.ProtocolError as e:
			logger.exception('exception')
			self._state = WorldState.disconnected
			self.emitter.emit(events.world.disconnected, reason=str(e))
			self._handling_packets = False
			raise e

	async def latency(self) -> datetime.timedelta:
		start = datetime.datetime.now()
		id = int32(int(uuid.uuid4()))
		await self.stream.send_encrypted_packet(CMSG_PING, make_CMSG_PING(id=id))

		pong = await self.wait_for_packet(Opcode.SMSG_PONG)
		if pong.ping != id:
			logger.warning(f'Server pong id mismatch: {pong.ping} != {id}')

		rtt = datetime.datetime.now() - start
		return int(rtt.total_seconds() * 1000)

	async def _loop_keepalive(self):
		assert self.state >= WorldState.in_game
		while True:
			await trio.sleep(5)
			await self.stream.send_encrypted_packet(CMSG_KEEP_ALIVE, make_CMSG_KEEP_ALIVE())
			await trio.sleep(25)

	async def _handle_time_sync_requests(self):
		assert self.state >= WorldState.in_game
		while True:
			request = await self.wait_for_packet(Opcode.SMSG_TIME_SYNC_REQ)
			ticks = int(1000 * time.time())
			await self.stream.send_encrypted_packet(CMSG_TIME_SYNC_RESP, make_CMSG_TIME_SYNC_RESP(
				id=request.id,
				client_ticks=ticks
			))

			self.emitter.emit(events.world.sent_time_sync, id=request.id, ticks=ticks)

	async def display_statistics(self):
		logger.info(f'Latency: {await self.latency()} ms, ')

	async def connect(self, realm=None, proxy=None, stream=None):
		if realm is not None:
			logger.info(f'Connecting to {realm.name} at {realm.address}')
		elif stream is not None:
			logger.info(f'Using {stream} as world stream.')

		if self._state > WorldState.not_connected:
			raise ProtocolError('Already connected to another realm!')

		if stream is None:
			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(
					destination=realm.address,
					proxy=proxy or self.proxy or None
				)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*realm.address)
		else:
			self._stream = stream

		self._realm = realm
		self._state = WorldState.connected
		self.emitter.emit(events.world.connected, self._realm.address)

	async def transfer(self, username, session_key):
		logger.info(f'Transferring {username} to world session {session_key}')
		if self.state < WorldState.connected:
			raise ProtocolError('Not connected to world server')

		self._state = WorldState.logging_in
		self.emitter.emit(events.world.logging_in)

		self.stream = WorldClientStream(stream=self._stream, session_key=session_key)
		self._username = username.upper()

		auth_challenge = await self.stream.receive_unencrypted_packet(SMSG_AUTH_CHALLENGE)
		if auth_challenge.header.opcode != Opcode.SMSG_AUTH_CHALLENGE:
			raise ProtocolError(f'Expected Opcode.SMSG_AUTH_CHALLENGE, but got {auth_challenge.header.opcode}')

		self._crypto = SessionCrypto(
			session_key,
			auth_challenge.server_seed,
			auth_challenge.encryption_seed1,
			auth_challenge.encryption_seed2
		)

		await self.stream.send_unencrypted_packet(CMSG_AUTH_SESSION, make_CMSG_AUTH_SESSION(
			account_name=self._username,
			client_seed=self._crypto.client_seed,
			account_hash=self._crypto.account_hash(self._username),
			realm_id=self._realm.id
		))

		self.warden = Warden(self, cr_files_path=Path('/home/fure/repos/warden_modules'))

		# self._store_packet, self.packets = trio.open_memory_channel(MAX_PACKET_QUEUE)
		await self._parent_nursery.start(self._packet_handler)
		auth_response = await self.wait_for_packet(Opcode.SMSG_AUTH_RESPONSE)

		if auth_response.response == AuthResponse.ok:
			self._state = WorldState.logged_in
			self.emitter.emit(events.world.logged_in)
			logger.info('Transfer complete')

		elif auth_response.response == AuthResponse.wait_queue:
			self._state = WorldState.in_queue
			self.emitter.emit(events.world.in_queue, auth_response.queue_position)
			logger.info('Transfer waiting')
			logger.info(f'In queue: {auth_response.queue_position}')

	async def characters(self) -> List[Character]:
		await self.stream.send_encrypted_packet(CMSG_CHAR_ENUM, make_CMSG_CHAR_ENUM())
		self.emitter.emit(events.world.sent_char_enum)

		char_enum = await self.wait_for_packet(Opcode.SMSG_CHAR_ENUM)
		return [Character(self, info) for info in char_enum.characters]

	@asynccontextmanager
	async def enter_world(self, character: CharacterInfo):
		logger.info(f'Entering world as {character.name}...')
		await self.stream.send_encrypted_packet(CMSG_PLAYER_LOGIN, make_CMSG_PLAYER_LOGIN(character.guid))
		self._state = WorldState.loading

		self.emitter.emit(events.world.sent_player_login)
		await self.wait_for_packet(Opcode.SMSG_LOGIN_VERIFY_WORLD)
		logger.info('Entered world')

		async with trio.open_nursery() as n:
			self.nursery = n
			try:
				self._state = WorldState.in_game
				self.chat = LocalChat(self)

				self.local_player = LocalPlayer(self, name=character.name, guid=character.guid, )
				self.emitter.emit(events.world.entered_world)
				n.start_soon(self._handle_time_sync_requests)
				n.start_soon(self._loop_keepalive)
				yield self.nursery

			except KeyboardInterrupt as e:
				raise e

			except Exception as e:
				logger.exception(e)

			finally:
				# if self.state >= WorldState.in_game:
				# 	await self.logout()
				self.nursery.cancel_scope.cancel()
				self._enter_character_select()

	async def logout(self):
		logger.info('Logging out...')
		self.emitter.emit(events.world.sent_logout_request)
		await self.stream.send_encrypted_packet(CMSG_LOGOUT_REQUEST, make_CMSG_LOGOUT_REQUEST())

		logout_response = await self.wait_for_packet(Opcode.SMSG_LOGOUT_RESPONSE)
		await self.wait_for_packet(Opcode.SMSG_LOGOUT_COMPLETE)

		self._enter_character_select()
		logger.info('Logged out')

	def _enter_character_select(self):
		self.chat = None
		self.local_player = None
		self._state = WorldState.logged_in
		self._handling_packets = False

__all__ = ['WorldSession', 'WorldState', 'SessionCrypto']