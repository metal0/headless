import random
import secrets
import traceback
from typing import Optional, Tuple

import trio
from trio_socks import socks5

from pont.client.world.net.protocol import WorldProtocol
from .character_select import CharacterInfo
from .errors import ProtocolError
from .net.handler import WorldHandler
from .net.packets.auth_packets import AuthResponse
from .. import events, world
from ..auth import Realm
from ...cryptography import sha

from ..log import mgr
log = mgr.get_logger(__name__)

class WorldSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]] = None):
		self.proxy = proxy
		self.protocol: Optional[WorldProtocol] = None
		self.handler: WorldHandler = WorldHandler(emitter)
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
		self._packets_received = []
		# self._world = esper.World

	def realm(self) -> Realm:
		return self._realm

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()

	async def characters(self) -> CharacterInfo:
		received_characters_event = trio.Event()
		characters: Optional[CharacterInfo] = None

		@self._emitter.once(events.world.received_SMSG_CHAR_ENUM)
		def on_char_enum(packet: world.net.packets.SMSG_CHAR_ENUM):
			nonlocal characters
			characters = packet.characters
			received_characters_event.set()

		await self.protocol.send_CMSG_CHAR_ENUM()
		await received_characters_event.wait()
		return characters

	async def _keepalive(self):
		log.debug('[_keepalive] started')
		while True:
			await self.protocol.send_CMSG_KEEP_ALIVE()
			self._emitter.emit(events.world.sent_CMSG_KEEP_ALIVE)
			r = random.betavariate(alpha=0.2, beta=0.7)
			random_factor = r * 20 - 10
			await trio.sleep(30 + random_factor)

	async def _ping_every_30_seconds(self):
		log.debug('[_ping_every_30_seconds] started')
		id = 0
		while True:
			await self.protocol.send_CMSG_PING(id)
			self._emitter.emit(events.world.sent_CMSG_PING)
			random_factor = random.betavariate(alpha=0.2, beta=0.7) * 20 - 10
			await trio.sleep(30 + random_factor)
			id += 1

	async def _packet_handler(self):
		log.debug('[_packet_handler] started')
		try:
			async for packet in self.protocol.process_packets():
				self.handler.handle(packet)

		except world.errors.ProtocolError as e:
			traceback.print_exc()
			self._emitter.emit(events.world.disconnected)
			await trio.lowlevel.checkpoint()
			raise e

	async def connect(self, realm: Realm, proxy=None, stream=None):
		log.info(f'Connecting to {realm.name} at {realm.address}')
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
		self._emitter.emit(events.world.connected, self._realm.address)

	async def authenticate(self, username, session_key):
		log.info(f'Logging in with username {username}...')
		self.protocol = WorldProtocol(stream=self._stream)
		self.protocol.init_encryption(session_key=session_key)
		self._session_key = session_key
		self._username = username.upper()

		auth_challenge = await self.protocol.receive_SMSG_AUTH_CHALLENGE()
		self._server_seed = auth_challenge.server_seed
		self._encryption_seed1 = auth_challenge.encryption_seed1
		self._encryption_seed2 = auth_challenge.encryption_seed2
		self._client_seed = secrets.randbits(32)
		account_hash = sha.sha1(
			self._username, bytes([0] * 4),
			self._client_seed,
			self._server_seed,
			self._session_key, out=int
		)

		await self.protocol.send_CMSG_AUTH_SESSION(
			account_name=self._username,
			client_seed=self._client_seed,
			account_hash=account_hash,
			realm_id=self._realm.id
		)

		response_event = trio.Event()
		@self._emitter.once(events.world.received_SMSG_AUTH_RESPONSE)
		def on_auth_response(packet: world.net.packets.SMSG_AUTH_RESPONSE):
			if packet.response == AuthResponse.ok:
				response_event.set()
				log.info('Logged in!')

			elif packet.response == AuthResponse.wait_queue:
				log.info(f'In queue: {packet.queue_position}')

		self._nursery.start_soon(self._packet_handler)
		await response_event.wait()

		# self._nursery.start_soon(self._keepalive)
		# self._nursery.start_soon(self._ping_every_30_seconds)
