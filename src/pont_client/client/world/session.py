import hashlib
import hmac
import random
import secrets
import trio

from trio_socks import socks5
from typing import Optional, Tuple
from arc4 import ARC4

from pont_client.client.world.net.protocol import WorldProtocol
from .net.packets.constants import Opcode
from .net.packets.headers import ServerHeader
from .. import log, events, world
from ..auth import Realm
from ...cryptography import sha
from ...cryptography.rc4 import RC4
from ...utility import construct
from ...utility.string import bytes_to_int, int_to_bytes

log = log.get_logger(__name__)

class WorldSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]] = None):
		self.proxy = proxy
		self.protocol: Optional[WorldProtocol] = None
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
		self._server_decrypt_key = bytes.fromhex('C2B3723CC6AED9B5343C53EE2F4367CE')
		self._client_encrypt_key = bytes.fromhex('CC98AE04E897EACA12DDC09342915357')
		self._encrypter = None
		self._decrypter = None
		self._client_key = None
		self._server_key = None
		self._encrypt = None
		self._decrypt = None
		# self._encrypt = lambda data: self._client_key.encrypt(b'\x00' * 1024 + data)
		# self._decrypt = lambda data: self._server_key.decrypt(b'\x00' * 1024 + data)
		# self._world = esper.World

	def realm(self) -> Realm:
		return self._realm

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()

	async def characters(self):
		pass

	async def _keepalive(self):
		log.debug('[_keepalive] started')
		while True:
			await self.protocol.send_CMSG_KEEP_ALIVE()
			self._emitter.emit(events.world.CMSG_KEEP_ALIVE_sent)
			r = random.betavariate(alpha=0.2, beta=0.7)
			random_factor = r * 20 - 10
			await trio.sleep(30 + random_factor)

	async def _ping_every_30_seconds(self):
		log.debug('[_ping_every_30_seconds] started')
		while True:
			await self.protocol.send_CMSG_PING()
			self._emitter.emit(events.world.CMSG_PING_sent)
			r = random.betavariate(alpha=0.2, beta=0.7)
			random_factor = r * 20 - 10
			await trio.sleep(30 + random_factor)

	async def _packet_handler(self):
		log.debug('[_packet_dispatcher] started')
		while True:
			packet = await self.protocol.receive_packet()
			log.debug(f'[_packet_dispatcher] received {packet=}')
			if packet is None or len(packet) == 0:
				raise ValueError('Empty stream')
			try:
				header = world.net.packets.parser.parse_header(packet)
				log.debug(f'[_packet_dispatcher] header: {header=}')
			except:
				pass

			if not self._decrypt is None:
				decrypted = self._decrypt(packet)
				log.debug(f'[_packet_dispatcher] {decrypted.hex()=}')

				if ((decrypted[0] & 0x80) == 0x80):
					next_byte = decrypted[4]
					size = (((decrypted[0] & 0x7F) << 16) | ((decrypted[1] & 0xFF) << 8) | (decrypted[2] & 0xFF)) - 2
					size = bytes_to_int(int_to_bytes(size)[::-1])
					opcode = (next_byte & 0xFF) << 8 | decrypted[3] & 0xFF
					opcode = bytes_to_int(int_to_bytes(opcode)[::-1])

					log.debug(f'[_packet_dispatcher] decrypted packet: {size=}, {hex(opcode)=}')

					opcode = bytes_to_int(int_to_bytes(opcode)[::-1])
					size = bytes_to_int(int_to_bytes(size)[::-1])
					log.debug(f'[_packet_dispatcher] decrypted packet: {size=}, {hex(opcode)=}')
				else:
					size = ((decrypted[0] & 0xFF) << 8 | decrypted[1] & 0xFF) - 2
					size = bytes_to_int(int_to_bytes(size)[::-1])
					opcode = (decrypted[3] & 0xFF) << 8 | decrypted[2] & 0xFF
					opcode = bytes_to_int(int_to_bytes(opcode)[::-1])
					log.debug(f'[_packet_dispatcher] decrypted packet: {size=}, {hex(opcode)=}')

					opcode = bytes_to_int(int_to_bytes(opcode)[::-1])
					size = bytes_to_int(int_to_bytes(size)[::-1])
					log.debug(f'[_packet_dispatcher] decrypted packet: {size=}, {hex(opcode)=}')

				# if (decrypted1[0] & 0x80):
				# 	decrypted2 = self._decrypt(packet[4:5])[0]
				# 	size = ((decrypted1[0] & 0x7F) << 16) | (decrypted1[1] << 8 ) | decrypted1[2]
				# 	opcode = Opcode(decrypted1[3] | (decrypted2 << 8))
				# else:
				# 	size = (decrypted1[0] << 8) | decrypted1[1]
				# 	opcode = Opcode(decrypted1[2] | (decrypted1[3] << 8))

				try:
					header = world.net.packets.parser.parse_header(decrypted)
					log.debug(f'[_packet_dispatcher] header: {header=}')
				except:
					pass

	async def connect(self, realm: Realm, proxy=None, stream=None):
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
		self.protocol = WorldProtocol(stream=self._stream)
		self._emitter.emit(events.world.connected, self._realm.address)

	async def authenticate(self, username, session_key):
		self._session_key = session_key
		self._username = username.upper()

		log.debug('waiting to receive SMSG_AUTH_CHALLENGE...')
		auth_challenge = await self.protocol.receive_SMSG_AUTH_CHALLENGE()

		log.debug(f'received SMSG_AUTH_CHALLENGE: {auth_challenge}')
		self._server_seed = auth_challenge.server_seed
		self._encryption_seed1 =  auth_challenge.encryption_seed1
		self._encryption_seed2 = auth_challenge.encryption_seed2

		self._client_seed = secrets.randbits(32)
		account_hash = sha.sha1(
			self._username, bytes([0, 0, 0, 0]),
			self._client_seed,
			self._server_seed,
			self._session_key, out=int
		)

		log.debug(f'{account_hash=}')
		await self.protocol.send_CMSG_AUTH_SESSION(
			account_name=self._username,
			client_seed=self._client_seed,
			account_hash=account_hash,
			realm_id=self._realm.id
		)

		client_hmac = hmac.new(key=self._client_encrypt_key, digestmod=hashlib.sha1)
		client_hmac.update(int_to_bytes(self._session_key))
		self._encrypter = RC4(client_hmac.digest())
		self._encrypter.encrypt(bytes([0]*1024))

		server_hmac = hmac.new(key=self._server_decrypt_key, digestmod=hashlib.sha1)
		server_hmac.update(int_to_bytes(self._session_key))
		self._decrypter = RC4(server_hmac.digest())
		self._decrypter.encrypt(bytes([0]*1024))

		self._encrypt = lambda data: self._encrypter.encrypt(data)
		self._decrypt = lambda data: self._decrypter.encrypt(data)

		# self._server_key = ARC4(
		# 	hmac.new(
		# 		key=self._server_decrypt_key,
		# 		msg=int_to_bytes(self._session_key),
		# 		digestmod=hashlib.sha1
		# 	).digest()
		# )
		#
		# self._client_key = ARC4(
		# 	hmac.new(
		# 		key=self._client_encrypt_key,
		# 		msg=int_to_bytes(self._session_key),
		# 		digestmod=hashlib.sha1
		# 	).digest()
		# )

		self._nursery.start_soon(self._packet_handler)
		# self._nursery.start_soon(self._keepalive)
		# self._nursery.start_soon(self._ping_every_30_seconds)
