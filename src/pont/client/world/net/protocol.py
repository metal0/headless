import hashlib
import hmac
import trio
import traceback

from construct import ConstructError
from ...cryptography import rc4
from ..errors import ProtocolError
from ..net import packets
from ..net.packets import headers
from ..net.packets.auth_packets import AuthResponse, default_addon_bytes
from ..net.packets.constants import Expansion, Opcode
from ..net.packets.headers import ServerHeader
from ..guid import Guid
from ... import log

log = log.mgr.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self._stream = stream
		self._server_decrypt_key = bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57])
		self._client_encrypt_key = bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE])
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()
		self._has_encryption = False
		self._encrypter = None
		self._decrypter = None

	async def process_packets(self):
		while True:
			# Receive header first
			async with self._read_lock:
				header_data = await self._stream.receive_some(max_bytes=4)

			if header_data is None or len(header_data) == 0:
				raise ProtocolError('received EOF from server')

			header_data = self.decrypt(header_data)
			if headers.is_large_packet(header_data):
				async with self._read_lock:
					header_data += self.decrypt(await self._stream.receive_some(max_bytes=1))

				size = ((header_data[0] & 0x7F) << 16) | (header_data[1] << 8) | header_data[2]
				opcode = Opcode(header_data[3] | (header_data[4] << 8))
				log.warning(f'[process_packets] large packet {size=}')

			else:
				size = (header_data[0] << 8) | header_data[1]
				opcode = Opcode(header_data[2] | (header_data[3] << 8))

			header_data = ServerHeader().build({
				'opcode': Opcode(opcode),
				'size': (0xFFFF & size)
			})

			header = packets.parser.parse_header(header_data)
			log.debug(f'{header=}')

			if header.size - 2 > 0:
				log.debug(f'Listening for {header.size - 2} bytes...')

				async with self._read_lock:
					data = header_data + await self._stream.receive_some(max_bytes=header.size - 2)

				if data is None or len(data) == 0:
					raise ProtocolError('received EOF from server')
			else:
				data = header_data

			await trio.lowlevel.checkpoint()

			try:
				packet = packets.parser.parse(data)
				yield packet

			except (KeyError, ConstructError) as e:
				await trio.lowlevel.checkpoint()
				if type(e) is KeyError:
					header = packets.parser.parse_header(header_data)
					log.warning(f'Dropped packet: {header=}')
				else:
					traceback.print_exc()

	def encrypt(self, data: bytes):
		if self.has_encryption():
			encrypted = self._encrypter.encrypt(data)
			return encrypted

		return data

	def decrypt(self, data: bytes):
		if self.has_encryption():
			decrypted = self._decrypter.decrypt(data)
			return decrypted

		return data

	def has_encryption(self):
		return self._has_encryption

	def encrypt_packet(self, data: bytes):
		header = data[0:6]
		return self.encrypt(header) + data[6:]

	def decrypt_packet(self, data: bytes):
		if data == None or len(data) == 0:
			return None

		if self.has_encryption():
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

	async def _receive_encrypted_packet(self, packet_name: str, packet):
		async with self._read_lock:
			packet = packet.parse(self.decrypt_packet(await self._stream.receive_some()))
			log.debug(f'[receive_{packet_name}] received decrypted: {packet}')
			return packet

	async def _receive_unencrypted_packet(self, packet_name: str, packet):
		async with self._read_lock:
			data = await self._stream.receive_some()
			packet = packet.parse(data)
			log.debug(f'[receive_{packet_name}] received unencrypted: {packet}')
			return packet

	async def _send_unencrypted_packet(self, packet_name: str, packet, **params):
		async with self._send_lock:
			data = packet.build(params)
			await self._stream.send_all(data)
			log.debug(f'[send_{packet_name}] sent unencrypted: {packet.parse(data)}')

	async def _send_encrypted_packet(self, packet_name: str, packet, **params):
		async with self._send_lock:
			data = packet.build(params)
			encrypted = self.encrypt_packet(data)
			await self._stream.send_all(encrypted)
			log.debug(f'[send_{packet_name}] sent encrypted: {packet.parse(data)}')

	def init_encryption(self, session_key: int):
		session_key_bytes = session_key.to_bytes(length=40, byteorder='little')
		client_hmac = hmac.new(key=self._client_encrypt_key, digestmod=hashlib.sha1)
		client_hmac.update(session_key_bytes)

		server_hmac = hmac.new(key=self._server_decrypt_key, digestmod=hashlib.sha1)
		server_hmac.update(session_key_bytes)
		self._encrypter = rc4.RC4(client_hmac.digest())
		self._encrypter.encrypt(bytes([0] * 1024))

		self._decrypter = rc4.RC4(server_hmac.digest())
		self._decrypter.encrypt(bytes([0] * 1024))
		self._has_encryption = True

	async def send_SMSG_AUTH_CHALLENGE(self, server_seed, encryption_seed1, encryption_seed2):
		"""
		Sends an unencrypted SMSG_AUTH_CHALLENGE packet.
		:param server_seed:
		:param encryption_seed1:
		:param encryption_seed2:
		:return: None.
		"""
		await self._send_unencrypted_packet(
			'SMSG_AUTH_CHALLENGE', packets.SMSG_AUTH_CHALLENGE,
			server_seed=server_seed,
			encryption_seed1=encryption_seed1,
			encryption_seed2=encryption_seed2
		)

	async def receive_SMSG_AUTH_CHALLENGE(self) -> packets.SMSG_AUTH_CHALLENGE:
		"""
		Receives an unencrypted SMSG_AUTH_CHALLENGE packet.
		:return: a parsed SMSG_AUTH_CHALLENGE packet.
		"""
		return await self._receive_unencrypted_packet('SMSG_AUTH_CHALLENGE', packets.SMSG_AUTH_CHALLENGE)

	async def send_CMSG_AUTH_SESSION(self, account_name, client_seed, account_hash, realm_id,
		build=12340, login_server_id=0, login_server_type=0, region_id=0, battlegroup_id=0, addon_info: bytes = default_addon_bytes):
		"""
		Sends an unencrypted CMSG_AUTH_SESSION packet.
		:return: None.
		"""
		await self._send_unencrypted_packet(
			'CMSG_AUTH_SESSION', packets.CMSG_AUTH_SESSION,
			build=build,
			login_server_id=login_server_id,
			account_name=account_name,
			login_server_type=login_server_type,
			client_seed=client_seed,
			region_id=region_id,
			battlegroup_id=battlegroup_id,
			realm_id=realm_id,
			account_hash=account_hash,
			addon_info=addon_info,
			header={'size': 61 + len(addon_info) + len(account_name)}
		)

	async def receive_CMSG_AUTH_SESSION(self) -> packets.CMSG_AUTH_SESSION:
		"""
		Receives an unencrypted CMSG_AUTH_SESSION packet.
		:return: a parsed CMSG_AUTH_SESSION packet.
		"""
		return await self._receive_unencrypted_packet(
			'CMSG_AUTH_SESSION', packets.CMSG_AUTH_SESSION
		)

	async def send_SMSG_AUTH_RESPONSE(self, response: AuthResponse, expansion: Expansion=Expansion.wotlk):
		"""
		Sends an encrypted SMSG_AUTH_RESPONSE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'SMSG_AUTH_RESPONSE', packets.SMSG_AUTH_RESPONSE,
			response=response, expansion=expansion
		)

	async def receive_SMSG_AUTH_RESPONSE(self) -> packets.SMSG_AUTH_RESPONSE:
		"""
		Receives an encrypted SMSG_AUTH_RESPONSE packet.
		:return: a parsed SMSG_AUTH_RESPONSE packet.
		"""
		return await self._receive_encrypted_packet(
			'SMSG_AUTH_RESPONSE', packets.SMSG_AUTH_RESPONSE
		)

	async def send_SMSG_WARDEN_DATA(self, command=51, module_id=0, module_key=0, size=100):
		"""
		Sends an encrypted SMSG_WARDEN_DATA packet.
		:param command:
		:param module_id:
		:param module_key:
		:param size:
		:return: None.
		"""
		await self._send_encrypted_packet(
			'SMSG_WARDEN_DATA', packets.SMSG_WARDEN_DATA,
			command=command,
			module_id=module_id,
			module_key=module_key,
			size=size
		)

	async def receive_SMSG_WARDEN_DATA(self) -> packets.SMSG_WARDEN_DATA:
		"""
		Receives an SMSG_WARDEN_DATA packet with optional encryption.
		:return: a parsed SMSG_WARDEN_DATA packet.
		"""
		return await self._receive_encrypted_packet('SMSG_WARDEN_DATA', packets.SMSG_WARDEN_DATA)

	async def send_CMSG_CHAR_ENUM(self):
		"""
		Sends an encrypted CMSG_CHAR_ENUM packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_CHAR_ENUM', packets.CMSG_CHAR_ENUM,
		)

	async def receive_SMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		"""
		Receives an encrypted SMSG_CHAR_ENUM packet.
		:return: a parsed SMSG_CHAR_ENUM packet.
		"""
		return await self._receive_encrypted_packet('SMSG_CHAR_ENUM', packets.SMSG_CHAR_ENUM)

	async def send_CMSG_PING(self, id, latency=60):
		"""
		Sends an encrypted CMSG_PING packet.
		:param id: the ping identifier (usually starts at 0 and increments)
		:param latency: the latency (in ms)
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_PING', packets.CMSG_PING,
			id=id, latency=latency
		)

	async def receive_CMSG_PING(self) -> packets.CMSG_PING:
		"""
		Receives an encrypted CMSG_PING packet.
		:return: a parsed CMSG_PING packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_PING', packets.CMSG_PING,
		)

	async def send_CMSG_KEEP_ALIVE(self):
		"""
		Sends a CMSG_KEEP_ALIVE packet with optional encryption.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_KEEP_ALIVE', packets.CMSG_KEEP_ALIVE,
		)

	async def receive_CMSG_KEEP_ALIVE(self):
		"""
		Receives and decrypts (if necessary) a CMSG_KEEP_ALIVE packet.
		:return: a parsed CMSG_KEEP_ALIVE packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_KEEP_ALIVE', packets.CMSG_KEEP_ALIVE,
		)

	async def send_CMSG_PLAYER_LOGIN(self, player_guid: Guid):
		"""
		Sends an encrypted CMSG_PLAYER_LOGIN packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_PLAYER_LOGIN', packets.CMSG_PLAYER_LOGIN,
			player_guid=player_guid
		)

	async def receive_CMSG_PLAYER_LOGIN(self) -> packets.CMSG_PLAYER_LOGIN:
		"""
		Receives an encrypted CMSG_PLAYER_LOGIN packet.
		:return: a parsed CMSG_PLAYER_LOGIN packet.
		"""
		return await self._receive_encrypted_packet('CMSG_PLAYER_LOGIN', packets.CMSG_PLAYER_LOGIN)

	async def send_CMSG_TIME_SYNC_RES(self, id, client_ticks):
		"""
		Sends an encrypted CMSG_TIME_SYNC_RES packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_TIME_SYNC_RES', packets.CMSG_TIME_SYNC_RESP,
			id=id,
			client_ticks=client_ticks,
		)

	async def receive_CMSG_TIME_SYNC_RES(self) -> packets.CMSG_TIME_SYNC_RESP:
		"""
		Receives an encrypted CMSG_TIME_SYNC_RES packet.
		:return: a parsed CMSG_TIME_SYNC_RES packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_TIME_SYNC_RES', packets.CMSG_TIME_SYNC_RESP,
		)

	async def receive_SMSG_CHATMESSAGE(self) -> packets.SMSG_MESSAGECHAT:
		"""
		Receives an encrypted SMSG_CHATMESSAGE packet.
		:return: a parsed SMSG_CHATMESSAGE packet.
		"""
		return await self._receive_encrypted_packet(
			'SMSG_CHATMESSAGE', packets.SMSG_MESSAGECHAT
		)