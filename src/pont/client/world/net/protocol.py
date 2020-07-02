import hashlib
import hmac
import traceback

import arc4
import trio

from pont.client.world.errors import ProtocolError
from pont.client.world.net import packets
from pont.client.world.net.packets import headers
from pont.client.world.net.packets.auth_packets import AuthResponse
from pont.client.world.net.packets.constants import Expansion, Opcode
from pont.client.world.net.packets.headers import ServerHeader
from ... import log
log = log.mgr.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._server_decrypt_key = bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57])
		self._client_encrypt_key = bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE])
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()
		self._has_encryption = False
		self._encrypter = None
		self._decrypter = None

	def encrypt(self, data: bytes):
		if self.has_encryption:
			self._encrypter.encrypt(bytes([0] * 1024))
			encrypted = self._encrypter.encrypt(data)
			log.debug(f'[encrypt] {encrypted=}')
			return encrypted

		return data

	def decrypt(self, data: bytes):
		if self.has_encryption:
			self._decrypter.decrypt(bytes([0] * 1024))
			decrypted = self._decrypter.decrypt(data)
			log.debug(f'[decrypt] {decrypted=}')
			return decrypted

		return data

	@property
	def has_encryption(self):
		return self._has_encryption

	def encrypt_packet(self, data: bytes):
		header = data[0:6]
		return self.encrypt(header) + data[6:]

	def decrypt_packet(self, data: bytes):
		if data == None or len(data) == 0:
			return None

		if self.has_encryption:
			decrypted = self.decrypt(data[0:4])
		else:
			decrypted = data[0:4]

		if headers.is_large_packet(decrypted):
			decrypted += bytes([self.decrypt(bytes([data[4]]))[0]])
			size = ((decrypted[0] & 0x7F) << 16) | (decrypted[1] << 8) | decrypted[2]
			log.warning(f'[decrypt_packet] large packet {size=}')

			opcode = Opcode(decrypted[3] | (decrypted[4] << 8))
			header = ServerHeader().build({
				'opcode': Opcode(opcode),
				'size': size
			})

			body = data[5:]
		else:
			size = (decrypted[0] << 8) | decrypted[1]
			opcode = Opcode(decrypted[2] | (decrypted[3] << 8))
			header = ServerHeader().build({
				'opcode': Opcode(opcode),
				'size': size
			})

			body = data[4:]

		data = header + body
		return data

	def init_encryption(self, session_key: int):
		session_key_bytes = session_key.to_bytes(length=40, byteorder='little')
		client_hmac = hmac.new(key=self._client_encrypt_key, digestmod=hashlib.sha1)
		client_hmac.update(session_key_bytes)

		server_hmac = hmac.new(key=self._server_decrypt_key, digestmod=hashlib.sha1)
		server_hmac.update(session_key_bytes)
		self._encrypter = arc4.ARC4(client_hmac.digest())
		# self._encrypter.encrypt(bytes([0] * 1024))

		self._decrypter = arc4.ARC4(server_hmac.digest())
		# self._decrypter.encrypt(bytes([0] * 1024))
		self._has_encryption = True

	async def send_SMSG_AUTH_CHALLENGE(self, server_seed, encryption_seed1, encryption_seed2):
		'''
		Sends an SMSG_AUTH_CHALLENGE packet with optional encrpytion.
		:param server_seed:
		:param encryption_seed1:
		:param encryption_seed2:
		:return: None.
		'''
		packet = packets.SMSG_AUTH_CHALLENGE.build({
			'server_seed': server_seed,
			'encryption_seed1': encryption_seed1,
			'encryption_seed2': encryption_seed2,
		})
		async with self._send_lock:
			await self.stream.send_all(packet)
		log.debug(f'[send_SMSG_AUTH_CHALLENGE] sent: {packets.SMSG_AUTH_CHALLENGE.parse(packet)}')

	async def receive_SMSG_AUTH_CHALLENGE(self) -> packets.SMSG_AUTH_CHALLENGE:
		'''
		Receives an SMSG_AUTH_CHALLENGE packet with optional encryption.
		:return: packet of type SMSG_AUTH_CHALLENGE.
		'''
		async with self._read_lock:
			packet = packets.SMSG_AUTH_CHALLENGE.parse(await self.stream.receive_some())
			log.debug(f'[receive_SMSG_AUTH_CHALLENGE] received: {packet}')
			return packet

	async def receive_SMSG_WARDEN_DATA(self) -> packets.SMSG_WARDEN_DATA:
		'''
		Receives an SMSG_WARDEN_DATA packet with optional encryption.
		:return: packet of type SMSG_WARDEN_DATA.
		'''
		async with self._read_lock:
			packet = packets.parser.parse(self.decrypt_packet(await self.stream.receive_some()))
			log.debug(f'[receive_SMSG_WARDEN_DATA] received: {packet}')
			return packet

	async def send_SMSG_WARDEN_DATA(self, command=51, module_id=0, module_key=0, size=100):
		'''
		Sends an SMSG_WARDEN_DATA packet with optional encryption.
		:param command:
		:param module_id:
		:param module_key:
		:param size:
		:return: None.
		'''
		data = self.encrypt_packet(packets.SMSG_WARDEN_DATA.build({
			'command': command,
			'module_id': module_id,
			'module_key': module_key,
			'size': size,
		}))
		async with self._send_lock:
			await self.stream.send_all(data)
		log.debug(f'[send_SMSG_WARDEN_DATA] sent packet: {packets.SMSG_WARDEN_DATA.parse(data)}')

	async def send_CMSG_AUTH_SESSION(self, account_name, client_seed, account_hash, realm_id,
		build=12340, login_server_id=0, login_server_type=0, region_id=0, battlegroup_id=0):
		'''
		Sends an unencrypted CMSG_AUTH_SESSION packet.
		:return: None.
		'''
		data = packets.CMSG_AUTH_SESSION.build({
			'build': build,
			'login_server_id': login_server_id,
			'account_name': account_name,
			'login_server_type': login_server_type,
			'client_seed': client_seed,
			'region_id': region_id,
			'battlegroup_id': battlegroup_id,
			'realm_id': realm_id,
			'account_hash': account_hash,
			'header': {'size': 61 + 237 + len(account_name)}
		})
		async with self._send_lock:
			await self.stream.send_all(data)
		log.debug(f'[send_CMSG_AUTH_SESSION] sent: {packets.CMSG_AUTH_SESSION.parse(data)}')

	async def receive_CMSG_AUTH_SESSION(self) -> packets.CMSG_AUTH_SESSION:
		'''
		Receives an unencrypted CMSG_AUTH_SESSION packet.
		:return: packet of type CMSG_AUTH_SESSION.
		'''
		async with self._read_lock:
			packet = packets.CMSG_AUTH_SESSION.parse(await self.stream.receive_some())
			log.debug(f'[receive_CMSG_AUTH_SESSION] received: {packet}')
			return packet

	async def send_SMSG_AUTH_RESPONSE(self, response: AuthResponse, expansion: Expansion=Expansion.wotlk):
		data = packets.SMSG_AUTH_RESPONSE.build({
			'response': response,
			'expansion': expansion,
		})

		packet = packets.SMSG_AUTH_RESPONSE.parse(data)
		async with self._read_lock:
			await self.stream.send_all(packet)
		log.debug(f'[send_SMSG_AUTH_RESPONSE] sent: {packet}')

	async def receive_SMSG_AUTH_RESPONSE(self) -> packets.SMSG_AUTH_RESPONSE:
		async with self._read_lock:
			packet = packets.SMSG_AUTH_RESPONSE.parse(await self.stream.receive_some())
			log.debug(f'[receive_SMSG_AUTH_RESPONSE] received: {packet}')
			return packet

	async def send_CMSG_CHAR_ENUM(self):
		'''
		Sends a CMSG_CHAR_ENUM packet with optional encryption.
		:return: None.
		'''
		data = packets.CMSG_CHAR_ENUM.build({})
		encrypted = self.encrypt_packet(data)
		async with self._send_lock:
			await self.stream.send_all(encrypted)
		log.debug(f'[send_CMSG_CHAR_ENUM] sent: {packets.CMSG_CHAR_ENUM.parse(data)}')

	async def receive_SMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		'''
		Receives an SMSG_CHAR_ENUM packet with optional encryption.
		:return: packet of type SMSG_CHAR_ENUM.
		'''
		async with self._read_lock:
			packet = packets.SMSG_CHAR_ENUM.parse(self.decrypt_packet(await self.stream.receive_some()))
			log.debug(f'[receive_SMSG_CHAR_ENUM] received: {packet}')
			return packet

	async def send_CMSG_PING(self, id, latency=60):
		'''
		Sends a CMSG_PING packet with optional encryption.
		:param id:
		:param latency:
		:return: None.
		'''
		data = packets.CMSG_PING.build({
			'id': id,
			'latency': latency
		})

		encrypted = self.encrypt_packet(data)
		async with self._send_lock:
			await self.stream.send_all(encrypted)
		log.debug(f'[send_CMSG_PING] sent: {packets.CMSG_PING.parse(data)}')

	async def send_CMSG_KEEP_ALIVE(self):
		'''
		Sends a CMSG_KEEP_ALIVE packet with optional encryption.
		:return: None.
		'''
		data = packets.CMSG_KEEP_ALIVE.build({})
		encrypted = self.encrypt_packet(data)
		async with self._send_lock:
			await self.stream.send_all(encrypted)
		log.debug(f'[send_CMSG_KEEP_ALIVE] sent: {packets.CMSG_KEEP_ALIVE.parse(data)}')

	async def process_packets(self):
		while True:
			# Receive header first
			async with self._read_lock:
				header_data = await self.stream.receive_some(max_bytes=4)

			if header_data is None or len(header_data) == 0:
				raise ProtocolError('received EOF from server')

			header_data = self.decrypt(header_data)
			log.debug(f'[process_packets] received: {header_data=}')

			if headers.is_large_packet(header_data):
				header_data += self.decrypt(await self.stream.receive_some(max_bytes=1))
				size = ((header_data[0] & 0x7F) << 16) | (header_data[1] << 8) | header_data[2]
				opcode = Opcode(header_data[3] | (header_data[4] << 8))
				log.warning(f'[decrypt_packet] large packet {size=}')

			else:
				size = (header_data[0] << 8) | header_data[1]
				opcode = Opcode(header_data[2] | (header_data[3] << 8))

			header_data = ServerHeader().build({
				'opcode': Opcode(opcode),
				'size': (0xFFFF & size)
			})

			header = packets.parser.parse_header(header_data)
			log.debug(f'{header=}')
			log.debug(f'Listening for {header.size - 2} bytes...')

			async with self._read_lock:
				data = header_data + await self.stream.receive_some(max_bytes=header.size - 2)

			if data is None or len(data) == 0:
				raise ProtocolError('received EOF from server')

			await trio.lowlevel.checkpoint()

			try:
				packet = packets.parser.parse(data)
				yield packet

			except KeyError:
				await trio.lowlevel.checkpoint()
				traceback.print_exc()
				header = packets.parser.parse_header(header_data)
				log.error(f'[receive_packet] Dropped packet: {header=}, {data=}')

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
