import random
from contextlib import asynccontextmanager
from typing import Optional, Tuple, Any, List

# import esper as esper
import trio
import pyee
from loguru import logger
from trio_socks import socks5

from pont.client.auth import Realm
from pont.client import events
from .names import NameCache
from .chat import Chat
from .errors import ProtocolError
from .net import WorldHandler, Opcode
from .net.packets import CharacterInfo
from .net.packets.auth_packets import AuthResponse
from .net.protocol import WorldClientProtocol
from .player import LocalPlayer
from .state import WorldState
from pont.client import world
from pont.cryptography import sha

class WorldCrypto:
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
			emitter = pyee.TrioEventEmitter(nursery=nursery)

		self.handler: WorldHandler = WorldHandler(emitter=emitter, world=self)
		self.emitter = emitter

		self.nursery: Optional[trio.Nursery] = None
		self.local_player: Optional[LocalPlayer] = None
		self.protocol: Optional[WorldClientProtocol] = None

		self._state = WorldState.not_connected
		self._parent_nursery = nursery
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._crypto: Optional[WorldCrypto] = None
		self._realm = None
		self._username = None
		self._handling_packets = False
		self.names = NameCache(self)

	@property
	def state(self):
		return self._state

	def realm(self) -> Realm:
		return self._realm

	async def aclose(self):
		if self._stream is not None:
			await self._stream.send_eof()
			await self._stream.aclose()

		self._handling_packets = False
		self._state = WorldState.not_connected

	# Wait for the given event under an optional condition to occur (once) and return a transform of the event keyword
	# arguments.
	async def wait_for_event(self, event, condition=None, result_transform=None) -> Any:
		receive_event = trio.Event()
		result = None
		if condition is None:
			condition = lambda **kwargs: True

		if result_transform is None:
			result_transform = lambda kwargs: kwargs

		async def on_event(**kwargs):
			if condition(**kwargs):
				nonlocal result
				result = result_transform(**kwargs)
				receive_event.set()

		listener = self.emitter.on(event, on_event)
		await receive_event.wait()

		self.emitter.remove_listener(event, listener)
		return result

	# Wait for a packet to be received under a certain condition and return it.
	async def wait_packet_condition(self, condition):
		if not self._handling_packets:
			raise ProtocolError('Packet handler not yet started')

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
		return await self.wait_packet_condition(lambda packet: packet.header.opcode == opcode)

	# Wait for a packet to be received and return it.
	async def wait_for_one_of(self, *opcodes: List[Opcode]) -> Any:
		return await self.wait_packet_condition(lambda packet: packet.header.opcode in opcodes)

	@staticmethod
	def _default_condition(**kwargs):
		return True

	async def _keepalive(self):
		logger.debug('started')
		while True:
			await self.protocol.send_CMSG_KEEP_ALIVE()
			self.emitter.emit(events.world.sent_keep_alive)
			r = random.betavariate(alpha=0.2, beta=0.7)
			random_factor = r * 20 - 10
			await trio.sleep(30 + random_factor)

	async def _packet_handler(self, *, task_status=trio.TASK_STATUS_IGNORED):
		task_status.started()
		logger.log('PACKETS', 'started')
		try:
			self._handling_packets = True
			async for packet in self.protocol.decrypted_packets():
				await self.handler.handle(packet)

		except world.ProtocolError as e:
			logger.exception('exception')
			self._state = WorldState.disconnected
			self.emitter.emit(events.world.disconnected, reason=str(e))
			await trio.lowlevel.checkpoint()
			self._handling_packets = False
			raise e

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

	# TODO: Write unit tests to test this function.
	#   Test the packet order and assert when our packet handler should be running
	#   Ensure self._parent_nursery.child_tasks contains a task whose name is _packet_hnadler.
	async def transfer(self, username, session_key):
		logger.info(f'Transferring {username} to world session {session_key}')
		if self.state < WorldState.connected:
			raise ProtocolError('Not connected to world server')

		self._state = WorldState.logging_in
		self.emitter.emit(events.world.logging_in)

		self.protocol = WorldClientProtocol(stream=self._stream, session_key=session_key)
		self._username = username.upper()

		auth_challenge = await self.protocol.receive_SMSG_AUTH_CHALLENGE()
		if auth_challenge.header.opcode != Opcode.SMSG_AUTH_CHALLENGE:
			raise ProtocolError(f'Expected Opcode.SMSG_AUTH_CHALLENGE, but got {auth_challenge.header.opcode}')

		self._crypto = WorldCrypto(
			session_key,
			auth_challenge.server_seed,
			auth_challenge.encryption_seed1,
			auth_challenge.encryption_seed2
		)

		await self.protocol.send_CMSG_AUTH_SESSION(
			account_name=self._username,
			client_seed=self._crypto.client_seed,
			account_hash=self._crypto.account_hash(self._username),
			realm_id=self._realm.id
		)

		await self._parent_nursery.start(self._packet_handler)
		auth_response = await self.wait_for_packet(Opcode.SMSG_AUTH_RESPONSE)

		if auth_response.response == AuthResponse.ok:
			self._state = WorldState.logged_in
			self.emitter.emit(events.world.logged_in)
			logger.info('Transfer complete')

		elif auth_response.response == AuthResponse.wait_queue:
			self._state = WorldState.in_queue
			self.emitter.emit(events.world.in_queue, auth_response.queue_position)
			logger.info('Transfer complete')
			logger.info(f'In queue: {auth_response.queue_position}')

	async def characters(self):
		await self.protocol.send_CMSG_CHAR_ENUM()
		self.emitter.emit(events.world.sent_char_enum)

		char_enum = await self.wait_for_packet(Opcode.SMSG_CHAR_ENUM)
		return char_enum.characters

	@asynccontextmanager
	async def enter_world(self, character: CharacterInfo):
		logger.info(f'Entering world as {character.name}...')
		await self.protocol.send_CMSG_PLAYER_LOGIN(character.guid)
		self._state = WorldState.loading

		self.emitter.emit(events.world.sent_player_login)
		await self.wait_for_packet(Opcode.SMSG_LOGIN_VERIFY_WORLD)
		logger.info('Entered world')

		async with trio.open_nursery() as n:
			self.nursery = n
			try:
				self._state = WorldState.in_game
				self.local_player = LocalPlayer(self, name=character.name, guid=character.guid)
				self.emitter.emit(events.world.entered_world)
				yield self.nursery

			except Exception as e:
				logger.exception(e)

			finally:
				# if self.state >= WorldState.in_game:
				# 	await self.logout()
				self.nursery.cancel_scope.cancel()

	async def logout(self):
		logger.info('Logging out...')
		self.emitter.emit(events.world.sent_logout_request)
		await self.protocol.send_CMSG_LOGOUT_REQUEST()

		logout_response = await self.wait_for_packet(Opcode.SMSG_LOGOUT_RESPONSE)
		await self.wait_for_packet(Opcode.SMSG_LOGOUT_COMPLETE)

		self.local_player = None
		self._state = WorldState.logged_in
		self._handling_packets = False
		logger.info('Logged out')

__all__ = ['WorldSession', 'WorldState', 'WorldCrypto']