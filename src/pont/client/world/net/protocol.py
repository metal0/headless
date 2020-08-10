import hashlib
import hmac
import random
from typing import Optional

import trio
import traceback

from construct import ConstructError

from .opcode import Opcode
from .packets.parse import WorldPacketParser
from ..chat.message import MessageType
from ..expansion import Expansion
from ..language import Language
from ...cryptography import rc4
from ..errors import ProtocolError, Disconnected
from ..net import packets
from ..net.packets import headers
from ..net.packets.auth_packets import AuthResponse, default_addon_bytes
from ..net.packets.headers import ServerHeader
from ..guid import Guid
from loguru import logger

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream, server: bool=False):
		self.stream = stream
		self.parser = WorldPacketParser()

		self._server_decrypt_key = bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57])
		self._client_encrypt_key = bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE])

		self._server_mode = server
		self._send_lock, self._read_lock = trio.Lock(), trio.Lock()

		self._has_encryption = False
		self._encrypter, self._decrypter = None, None

		self._num_packets_received = 0
		self._num_packets_sent = 0

	@property
	def num_packets_sent(self):
		return self._num_packets_sent

	@property
	def num_packets_received(self):
		return self._num_packets_received

	async def process_packets(self):
		while True:
			# Receive header first
			async with self._read_lock:
				header_data = await self.stream.receive_some(max_bytes=4)

			if header_data is None or len(header_data) == 0:
				raise Disconnected('received EOF from server')

			header_data = self.decrypt(header_data)
			try:
				if headers.is_large_packet(header_data):
					async with self._read_lock:
						header_data += self.decrypt(await self.stream.receive_some(max_bytes=1))

					size = ((header_data[0] & 0x7F) << 16) | (header_data[1] << 8) | header_data[2]
					opcode = Opcode(header_data[3] | (header_data[4] << 8))
					logger.warning(f'[process_packets] large packet {size=}')

				else:
					size = (header_data[0] << 8) | header_data[1]
					opcode = Opcode(header_data[2] | (header_data[3] << 8))

				header_data = ServerHeader().build({
					'opcode': Opcode(opcode),
					'size': (0xFFFF & size)
				})
			except ValueError as e:
				if 'is not a valid Opcode' in str(e):
					raise ProtocolError('Invalid opcode, stream might be out of sync')

			header = self.parser.parse_header(header_data)
			logger.log('PACKETS', f'{header=}')

			if header.size - 2 > 0:
				logger.log('PACKETS', f'Listening for {header.size - 2} bytes...')

				async with self._read_lock:
					data = header_data + await self.stream.receive_some(max_bytes=header.size - 2)

				if data is None or len(data) == 0:
					raise ProtocolError('received EOF from server')
			else:
				data = header_data

			await trio.lowlevel.checkpoint()
			logger.log('PACKETS', f'{data=}')

			try:
				packet = self.parser.parse(data)
				yield packet
				self._num_packets_received += 1

			except (KeyError, ConstructError) as e:
				await trio.lowlevel.checkpoint()
				if type(e) is KeyError:
					header = self.parser.parse_header(header_data)
					logger.log('PACKETS', f'Dropped packet: {header=}')
				else:
					traceback.print_exc()

	def encrypt(self, data: bytes):
		if self.has_encryption():
			encrypted = self._encrypter.encrypt(data)
			return encrypted

		return data

	def decrypt(self, data: bytes):
		if self.has_encryption():
			decrypted = self._decrypter.encrypt(data)
			return decrypted

		return data

	def has_encryption(self):
		return self._has_encryption

	def _encrypt_packet(self, data: bytes):
		header = data[0:6]
		return self.encrypt(header) + data[6:]

	def _decrypt_packet(self, data: bytes):
		if data is None or len(data) == 0:
			return None

		if self.has_encryption():
			decrypted = self.decrypt(data[0:4])
		else:
			decrypted = data[0:4]

		if headers.is_large_packet(decrypted):
			decrypted += bytes([self.decrypt(bytes([data[4]]))[0]])
			size = ((decrypted[0] & 0x7F) << 16) | (decrypted[1] << 8) | decrypted[2]
			logger.warning(f'[decrypt_packet] large packet {size=}')

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
			data = self._decrypt_packet(await self.stream.receive_some())
			packet = packet.parse(data)
			logger.log('PACKETS', f'{packet_name}: {packet}')
			logger.log('PACKETS', f'{data=}')
			self._num_packets_received += 1
			return packet

	async def _receive_unencrypted_packet(self, packet_name: str, packet):
		async with self._read_lock:
			data = await self.stream.receive_some()
			packet = packet.parse(data)
			logger.log('PACKETS', f'{packet_name}: {packet}')
			logger.log('PACKETS', f'{data=}')
			self._num_packets_received += 1
			return packet

	async def _send_unencrypted_packet(self, packet_name: str, packet, **params):
		async with self._send_lock:
			data = packet.build(params)
			await self.stream.send_all(data)
			logger.log('PACKETS', f'{packet_name}: {packet.parse(data)}')
			logger.log('PACKETS', f'{data=}')
			self._num_packets_sent += 1

	async def _send_encrypted_packet(self, packet_name: str, packet, **params):
		async with self._send_lock:
			data = packet.build(params)
			encrypted = self._encrypt_packet(data)
			await self.stream.send_all(encrypted)
			logger.log('PACKETS', f'{packet_name}: {packet.parse(data)}')
			logger.log('PACKETS', f'{data=}')
			self._num_packets_sent += 1

	def init_encryption(self, session_key: int):
		session_key_bytes = session_key.to_bytes(length=40, byteorder='little')
		client_hmac = hmac.new(key=self._client_encrypt_key, digestmod=hashlib.sha1)
		client_hmac.update(session_key_bytes)

		server_hmac = hmac.new(key=self._server_decrypt_key, digestmod=hashlib.sha1)
		server_hmac.update(session_key_bytes)

		if not self._server_mode:
			decrypt_hmac, encrypt_hmac = server_hmac, client_hmac
		else:
			decrypt_hmac, encrypt_hmac = client_hmac, server_hmac

		self._encrypter = rc4.RC4(encrypt_hmac.digest())
		self._encrypter.encrypt(bytes([0] * 1024))

		self._decrypter = rc4.RC4(decrypt_hmac.digest())
		self._decrypter.encrypt(bytes([0] * 1024))
		self._has_encryption = True

	async def send_SMSG_AUTH_CHALLENGE(self, server_seed: int=random.getrandbits(32), encryption_seed1: int=random.getrandbits(16), encryption_seed2: int=random.getrandbits(16)):
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

	async def send_SMSG_AUTH_RESPONSE(self, response: AuthResponse, expansion: Expansion=Expansion.wotlk, queue_position: Optional[int]=None):
		"""
		Sends an encrypted SMSG_AUTH_RESPONSE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'SMSG_AUTH_RESPONSE', packets.SMSG_AUTH_RESPONSE,
			response=response, expansion=expansion,
			queue_position=queue_position
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

	async def receive_CMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		"""
		Receives an encrypted CMSG_CHAR_ENUM packet.
		:return: a parsed CMSG_CHAR_ENUM packet.
		"""
		return await self._receive_encrypted_packet('CMSG_CHAR_ENUM', packets.CMSG_CHAR_ENUM)

	async def send_SMSG_CHAR_ENUM(self):
		"""
		Sends an encrypted SMSG_CHAR_ENUM packet.
		:return: None.
		"""
		await self._send_encrypted_packet('SMSG_CHAR_ENUM', packets.SMSG_CHAR_ENUM)

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

	async def receive_CMSG_PLAYER_LOGIN(self):
		"""
		Receives an encrypted CMSG_PLAYER_LOGIN packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_PLAYER_LOGIN', packets.CMSG_PLAYER_LOGIN
		)

	async def send_CMSG_LOGOUT_REQUEST(self):
		"""
		Sends an encrypted CMSG_LOGOUT_REQUEST packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_LOGOUT_REQUEST', packets.CMSG_LOGOUT_REQUEST
		)

	async def receive_CMSG_LOGOUT_REQUEST(self):
		"""
		Receives an encrypted CMSG_LOGOUT_REQUEST packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_LOGOUT_REQUEST', packets.CMSG_LOGOUT_REQUEST
		)

	async def send_CMSG_DUEL_ACCEPTED(self):
		"""
		Sends an encrypted CMSG_DUEL_ACCEPTED packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_DUEL_ACCEPTED', packets.CMSG_DUEL_ACCEPTED
		)

	async def receive_CMSG_DUEL_ACCEPTED(self) -> packets.CMSG_DUEL_ACCEPTED:
		"""
		Receives an encrypted CMSG_DUEL_ACCEPTED packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_DUEL_ACCEPTED', packets.CMSG_DUEL_ACCEPTED
		)

	async def send_CMSG_GUILD_ROSTER(self):
		"""
		Sends an encrypted CMSG_GUILD_ROSTER packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GUILD_ROSTER', packets.CMSG_GUILD_ROSTER
		)

	async def receive_CMSG_GUILD_ROSTER(self) -> packets.CMSG_GUILD_ROSTER:
		"""
		Receives an encrypted CMSG_GUILD_ROSTER packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_GUILD_ROSTER', packets.CMSG_GUILD_ROSTER
		)

	async def send_CMSG_GUILD_ACCEPT(self):
		"""
		Sends an encrypted CMSG_GUILD_ACCEPT packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GUILD_ACCEPT', packets.CMSG_GUILD_ACCEPT
		)

	async def receive_CMSG_GUILD_ACCEPT(self) -> packets.CMSG_GUILD_ACCEPT:
		"""
		Receives an encrypted CMSG_GUILD_ACCEPT packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_GUILD_ACCEPT', packets.CMSG_GUILD_ACCEPT
		)

	async def send_CMSG_GUILD_SET_PUBLIC_NOTE(self, player: str, note: str):
		"""
		Sends an encrypted CMSG_GUILD_SET_PUBLIC_NOTE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GUILD_SET_PUBLIC_NOTE', packets.CMSG_GUILD_SET_PUBLIC_NOTE,
			player=player,
			note=note
		)

	async def receive_CMSG_GUILD_SET_PUBLIC_NOTE(self) -> packets.CMSG_GUILD_SET_PUBLIC_NOTE:
		"""
		Receives an encrypted CMSG_GUILD_SET_PUBLIC_NOTE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet('CMSG_GUILD_SET_PUBLIC_NOTE', packets.CMSG_GUILD_SET_PUBLIC_NOTE)

	async def send_CMSG_GUILD_DECLINE(self):
		"""
		Sends an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GUILD_DECLINE', packets.CMSG_GUILD_DECLINE
		)

	async def receive_CMSG_GUILD_DECLINE(self) -> packets.CMSG_GUILD_DECLINE:
		"""
		Receives an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet('CMSG_GUILD_DECLINE', packets.CMSG_GUILD_DECLINE)

	async def send_SMSG_GUILD_INVITE(self, inviter: str, guild: str):
		"""
		Sends an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'SMSG_GUILD_INVITE', packets.SMSG_GUILD_INVITE,
			header={'size': len(inviter) + len(guild) + 2},
			inviter=inviter,
			guild=guild
		)

	async def receive_SMSG_GUILD_INVITE(self) -> packets.SMSG_GUILD_INVITE:
		"""
		Receives an encrypted SMSG_GUILD_INVITE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet('SMSG_GUILD_INVITE', packets.SMSG_GUILD_INVITE)

	async def send_CMSG_GUILD_CREATE(self, guild_name: str):
		"""
		Sends an encrypted CMSG_GUILD_CREATE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GUILD_CREATE', packets.CMSG_GUILD_CREATE,
			header={'size': len(guild_name) + 4},
			guild_name=guild_name
		)

	async def receive_CMSG_GUILD_CREATE(self) -> packets.CMSG_GUILD_CREATE:
		"""
		Receives an encrypted CMSG_GUILD_CREATE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_GUILD_CREATE', packets.CMSG_GUILD_CREATE
		)

	async def send_CMSG_LOGOUT_CANCEL(self):
		"""
		Sends an encrypted CMSG_LOGOUT_CANCEL packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_LOGOUT_CANCEL', packets.CMSG_LOGOUT_CANCEL
		)

	async def receive_CMSG_LOGOUT_CANCEL(self) -> packets.CMSG_LOGOUT_CANCEL:
		"""
		Receives an encrypted CMSG_LOGOUT_CANCEL packet.
		:return: a parsed CMSG_LOGOUT_CANCEL packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_LOGOUT_CANCEL', packets.CMSG_LOGOUT_CANCEL
		)

	async def send_CMSG_GROUP_ACCEPT(self):
		"""
		Sends an encrypted CMSG_GROUP_ACCEPT packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GROUP_ACCEPT', packets.CMSG_GROUP_ACCEPT
		)

	async def send_CMSG_GROUP_INVITE(self, invitee: str):
		"""
		Sends an encrypted CMSG_GROUP_INVITE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_GROUP_INVITE', packets.CMSG_GROUP_INVITE,
			header={'size': len(invitee) + 4},
			invitee=invitee,
			unknown=0,
		)

	async def receieve_CMSG_GROUP_INVITE(self) -> packets.CMSG_GROUP_INVITE:
		"""
		Receives an encrypted CMSG_GROUP_INVITE packet.
		:return: a parsed CMSG_GROUP_INVITE packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_GROUP_INVITE',
			packets.CMSG_GROUP_INVITE
		)

	async def send_SMSG_GROUP_INVITE(self, inviter: str, in_group=False):
		"""
		Sends an encrypted SMSG_GROUP_INVITE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'SMSG_GROUP_INVITE', packets.SMSG_GROUP_INVITE,
			header={'size': 1 + len(inviter) + 4 + 1 + 4},
			in_group=in_group,
			inviter=inviter
		)

	async def receieve_SMSG_GROUP_INVITE(self) -> packets.SMSG_GROUP_INVITE:
		"""
		Receives an encrypted SMSG_GROUP_INVITE packet.
		:return: a parsed SMSG_GROUP_INVITE packet.
		"""
		return await self._receive_encrypted_packet(
			'SMSG_GROUP_INVITE',
			packets.SMSG_GROUP_INVITE
		)

	async def send_CMSG_TIME_SYNC_RES(self, id: int, client_ticks: int):
		"""
		Sends an encrypted CMSG_TIME_SYNC_RES packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			'CMSG_TIME_SYNC_RES', packets.CMSG_TIME_SYNC_RESP,
			id=id, client_ticks=(client_ticks & 0xFFFFFFFF),
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

	async def send_CMSG_MESSAGECHAT(self,
		text: str, message_type: MessageType=MessageType.say,
		language=Language.universal, receiver: Optional[str]=None,
		channel: Optional[str]=None
	):
		"""
		Sends an encrypted CMSG_MESSAGECHAT packet.
		:return: None.
		"""
		size = 4 + 4 + len(text)
		if message_type in (MessageType.whisper, MessageType.channel):
			size += max(len(channel), len(receiver))

		await self._send_encrypted_packet(
			'CMSG_MESSAGECHAT', packets.CMSG_MESSAGECHAT,
			header={'size': size + 5},
			text=text, message_type=message_type, language=language,
			receiver=receiver, channel=channel
		)

	async def receieve_CMSG_MESSAGECHAT(self,
		message: str, message_type: MessageType=MessageType.say,
		language=Language.universal, receiver: Optional[str]=None,
		channel: Optional[str]=None
	):
		"""
		Sends an encrypted CMSG_MESSAGECHAT packet.
		:return: None.
		"""
		size = 4 + 4 + len(message)
		if message_type in (MessageType.whisper, MessageType.channel):
			size += max(len(channel), len(receiver))

		await self._receive_encrypted_packet(
			'CMSG_MESSAGECHAT', packets.CMSG_MESSAGECHAT,
		)
