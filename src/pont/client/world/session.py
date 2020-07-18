import random
from typing import Optional, Tuple, Any

import esper as esper
import trio
from trio_socks import socks5

from pont.client.cryptography import sha
from .character_select import CharacterInfo
from .errors import ProtocolError
from .net import WorldHandler, WorldProtocol, Opcode
from .net.packets.auth_packets import AuthResponse
from .. import events, world
from ..auth import Realm
from ...utility.enum import ComparableEnum
from loguru import logger

class WorldSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]] = None):
		self.proxy = proxy
		self.protocol: Optional[WorldProtocol] = None
		self.handler: WorldHandler = WorldHandler(emitter=emitter, world=self)
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._session_key = None
		self._realm = None
		self._client_seed = None
		self._server_seed = None
		self._encryption_seed1 = None
		self._encryption_seed2 = None
		self._username = None
		self._state = WorldState.not_connected

	@property
	def state(self):
		return self._state

	def realm(self) -> Realm:
		return self._realm

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()

		self._state = WorldState.not_connected

	async def wait_for_packet(self, opcode: Opcode) -> Any:
		receive_event = trio.Event()
		result = None

		async def on_receive_packet(packet):
			if packet.header.opcode == opcode:
				nonlocal result
				result = packet
				receive_event.set()

		listener = self._emitter.on(events.world.received_packet, on_receive_packet)
		await receive_event.wait()

		self._emitter.remove_listener(events.world.received_packet, listener)
		return result

	async def _keepalive(self):
		logger.debug('started')
		while True:
			await self.protocol.send_CMSG_KEEP_ALIVE()
			self._emitter.emit(events.world.sent_CMSG_KEEP_ALIVE)
			r = random.betavariate(alpha=0.2, beta=0.7)
			random_factor = r * 20 - 10
			await trio.sleep(30 + random_factor)

	# async def ping(self) -> int:
	# 	await self.protocol.send_CMSG_PING()

	# async def _ping_every_30_seconds(self):
	# 	logger.debug('[_ping_every_30_seconds] started')
	# 	id = 0
	# 	while True:
	# 		await self.protocol.send_CMSG_PING(id)
	# 		self._emitter.emit(events.world.sent_CMSG_PING)
	# 		random_factor = random.betavariate(alpha=0.2, beta=0.7) * 20 - 10
	# 		await trio.sleep(30 + random_factor)
	# 		id += 1

	async def _packet_handler(self):
		logger.debug('started')
		try:
			async for packet in self.protocol.process_packets():
				self._emitter.emit(events.world.received_packet, packet=packet)
				await self.handler.handle(packet)

		except world.ProtocolError as e:
			logger.exception('packet handler exception')
			self._state = WorldState.disconnected
			self._emitter.emit(events.world.disconnected, reason=str(e))
			await trio.lowlevel.checkpoint()
			raise e

	async def connect(self, realm=None, proxy=None, stream=None):
		if realm is not None:
			logger.info(f'Connecting to {realm.name} at {realm.address}')
		elif stream is not None:
			logger.info(f'Using {stream} as world stream.')

		if self._state > WorldState.not_connected:
			raise ProtocolError('Already connected to another server!')

		if stream is None:
			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(destination=realm.address,
				                                   proxy=proxy or self.proxy or None)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*realm.address)
		else:
			self._stream = stream

		self._realm = realm
		self._state = WorldState.connected
		self._emitter.emit(events.world.connected, self._realm.address)

	async def authenticate(self, username, session_key):
		logger.info(f'Logging in with username {username}...')
		if self.state < WorldState.connected:
			raise ProtocolError('Not connected to world server')

		self._state = WorldState.logging_in
		self._emitter.emit(events.world.logging_in)

		self.protocol = WorldProtocol(stream=self._stream)
		self.protocol.init_encryption(session_key=session_key)
		self._session_key = session_key
		self._username = username.upper()

		auth_challenge = await self.protocol.receive_SMSG_AUTH_CHALLENGE()
		self._server_seed = auth_challenge.server_seed
		self._encryption_seed1 = auth_challenge.encryption_seed1
		self._encryption_seed2 = auth_challenge.encryption_seed2

		self._client_seed = random.getrandbits(32)
		account_hash = sha.sha1(
			self._username, bytes([0] * 4),
			self._client_seed,
			self._server_seed,
			self._session_key, out=int
		)

		self._emitter.emit(events.world.sent_CMSG_AUTH_SESSION)
		await self.protocol.send_CMSG_AUTH_SESSION(
			account_name=self._username,
			client_seed=self._client_seed,
			account_hash=account_hash,
			realm_id=self._realm.id
		)

		self._nursery.start_soon(self._packet_handler)
		auth_response = await self.wait_for_packet(Opcode.SMSG_AUTH_RESPONSE)

		if auth_response.response == AuthResponse.ok:
			self._state = WorldState.logged_in
			logger.info('Logged in!')

		elif auth_response.response == AuthResponse.wait_queue:
			self._state = WorldState.in_queue
			logger.info(f'In queue: {auth_response.queue_position}')

		self._nursery.start_soon(self._keepalive)

	async def characters(self):
		await self.protocol.send_CMSG_CHAR_ENUM()
		self._emitter.emit(events.world.sent_CMSG_CHAR_ENUM)

		char_enum = await self.wait_for_packet(Opcode.SMSG_CHAR_ENUM)
		return char_enum.characters

	async def enter_world(self, character: CharacterInfo):
		logger.info(f'Entering world as {character.name}...')
		await self.protocol.send_CMSG_PLAYER_LOGIN(character.guid)

		self._emitter.emit(events.world.sent_CMSG_PLAYER_LOGIN)
		await self.wait_for_packet(Opcode.SMSG_LOGIN_VERIFY_WORLD)

		self._emitter.emit(events.world.entered_world)
		self._state = WorldState.in_game
		logger.info('Entered world')

	async def logout(self):
		logger.debug('logout called')
		self._emitter.emit(events.world.sent_CMSG_LOGOUT_REQUEST)
		await self.protocol.send_CMSG_LOGOUT_REQUEST()

		logout_response = await self.wait_for_packet(Opcode.SMSG_LOGOUT_RESPONSE)
		await self.wait_for_packet(Opcode.SMSG_LOGOUT_COMPLETE)
		self._state = WorldState.logged_in

class WorldState(ComparableEnum):
	disconnected = -1
	not_connected = 0
	connected = 1
	logging_in = 2
	in_queue = 3
	logged_in = 4

	loading = 5
	in_game = 6

__all__ = ['WorldSession', 'WorldState']