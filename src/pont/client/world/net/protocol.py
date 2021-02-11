import collections
import hashlib
import hmac
import random
import traceback
from typing import Optional, List

import trio
from construct import ConstructError
from loguru import logger

from pont.utility.construct import int8, GuidUnpacker, compute_packed_guid_byte_size, unpack_guid, pack_guid
from .opcode import Opcode
from .packets import parse
from .packets.name_query import NameInfo
from .packets.parse import WorldPacketParser, WorldServerPacketParser, WorldClientPacketParser
from ..chat.message import MessageType
from ..errors import ProtocolError, Disconnected
from ..expansions import Expansion
from ..guid import Guid
from ..language import Language
from ..net import packets
from ..net.packets import headers
from ..net.packets.auth_packets import AuthResponse, default_addon_bytes
from ..net.packets.headers import ServerHeader, ClientHeader
from pont.cryptography import rc4

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int, encryption_key: bytes, decryption_key: bytes):
		self._stream = stream

		self._encryption_key = encryption_key
		self._decryption_key = decryption_key

		self._send_lock, self._read_lock = trio.StrictFIFOLock(), trio.StrictFIFOLock()

		self._has_encryption = False
		self._encrypter, self._decrypter = None, None
		self._num_packets_received = 0
		self._num_packets_sent = 0

		self._init_encryption(session_key)

	@property
	def num_packets_sent(self):
		return self._num_packets_sent

	@property
	def num_packets_received(self):
		return self._num_packets_received

	def _init_encryption(self, session_key: int):
		session_key_bytes = session_key.to_bytes(length=40, byteorder='little')
		encrypt_hmac = hmac.new(key=self._encryption_key, digestmod=hashlib.sha1)
		encrypt_hmac.update(session_key_bytes)

		decrypt_hmac = hmac.new(key=self._decryption_key, digestmod=hashlib.sha1)
		decrypt_hmac.update(session_key_bytes)

		self._encrypter = rc4.RC4(encrypt_hmac.digest())
		self._encrypter.encrypt(bytes([0] * 1024))

		self._decrypter = rc4.RC4(decrypt_hmac.digest())
		self._decrypter.encrypt(bytes([0] * 1024))
		self._has_encryption = True

	def encrypt_packet(self, data: bytes, header):
		raise NotImplemented()

	def decrypt_packet(self, data: bytes):
		raise NotImplemented()

	def enable_encryption(self):
		self._has_encryption = True

	def disable_encryption(self):
		self._has_encryption = False

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

	async def send_all(self, data: bytes):
		async with self._send_lock:
			result = await self._stream.send_all(data)
			return result

	async def receive_some(self, max_bytes=None) -> bytes:
		async with self._read_lock:
			result = await self._stream.receive_some(max_bytes)
			if type(result) is not bytes:
				return bytes(result)
			return result

	async def next_decrypted_packet(self):
		raise NotImplemented()

	async def decrypted_packets(self):
		while True:
			try:
				packet = await self.next_decrypted_packet()
				yield packet
			except KeyError as e:
				logger.log('PACKETS', f'Dropped {e}')

	async def _receive_encrypted_packet(self, packet):
		data = self.decrypt_packet(await self.receive_some())
		packet = packet.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{type(packet)=}')
		# logger.log('PACKETS', packet)
		# logger.log('PACKETS', f'{data=}')
		return packet

	async def _receive_unencrypted_packet(self, packet_type):
		data = await self.receive_some()
		packet_type = packet_type.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{packet_type=}')
		return packet_type

	async def _send_unencrypted_packet(self, packet_type, **params):
		data = packet_type.build(params)
		await self.send_all(data)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{packet_type=}')
		# logger.log('PACKETS', f'{data=}')

	async def _send_encrypted_packet(self, packet_type, **params):
		data = packet_type.build(params)
		packet = packet_type.parse(data)
		encrypted = self.encrypt_packet(data, packet.header)
		await self.send_all(encrypted)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{len(data)=}')
		# logger.log('PACKETS', f'{packet_name}: {packet}')
		logger.log('PACKETS', f'{data[:min(len(data), 50)]=} {encrypted[:min(len(data), 50)]=}')

class WorldClientProtocol(WorldProtocol):
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int):
		super().__init__(stream, session_key,
            encryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
			decryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
		)

		self.parser = WorldServerPacketParser()

	def decrypt_packet(self, data: bytes):
		# logger.debug(f'(Client) {data=}')
		if data is None or len(data) == 0:
			return None

		start = self.decrypt(bytes([data[0]]))
		body_start = 5 if headers.is_large_server_packet(start) else 4
		rest = self.decrypt(data[1:body_start])
		return (start + rest) + data[body_start:]

	def encrypt_packet(self, data: bytes, header):
		# logger.debug(f'(Client) {data=}')
		return self.encrypt(data[0:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self.receive_some(max_bytes=4)

		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from server')

		logger.log('PACKETS', f'(Client) Incoming packet...')
		logger.log('PACKETS', f'{original_data=}')

		try:
			header_data = self.decrypt(original_data[0:4])
			is_large = headers.is_large_server_packet(header_data)

			if is_large:
				header_data += self.decrypt(await self.receive_some(max_bytes=1))

			logger.log('PACKETS', f'{header_data=}')
			header = ServerHeader().parse(header_data)
			logger.log('PACKETS', f'{header=}')
			data = header_data

			# TODO: Fix this header size bug for certain packets??
			bytes_left = header.size - 2
			while bytes_left > 0:
				logger.log('PACKETS', f'Listening for {bytes_left} byte body...')
				leftover_bytes = await self.receive_some(max_bytes=bytes_left)
				logger.log('PACKETS', f'{len(leftover_bytes)=}')
				# if len(leftover_bytes) != bytes_left:
				# 	logger.warning(f'Body data incomplete: {len(leftover_bytes)=} {bytes_left=}')
					# raise ProtocolError('Header size does not match body length')

				data += leftover_bytes
				bytes_left -= len(leftover_bytes)

				if leftover_bytes is None or len(leftover_bytes) == 0:
					raise ProtocolError('received EOF from server')

			try:
				packet = self.parser.parse(data, header)
				self._num_packets_received += 1
				return packet
			except KeyError:
				self._num_packets_received += 1
				raise KeyError(header)

		except ValueError as e:
			if 'is not a valid Opcode' in str(e):
				raise ProtocolError('Invalid opcode, stream might be out of sync')

	async def send_CMSG_AUTH_SESSION(self, account_name, client_seed, account_hash, realm_id,
		build=12340, login_server_id=0, login_server_type=0, region_id=0, battlegroup_id=0, addon_info: bytes = default_addon_bytes):
		"""
		Sends an unencrypted CMSG_AUTH_SESSION packet.
		:return: None.
		"""
		await self._send_unencrypted_packet(
			packets.CMSG_AUTH_SESSION,
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

	async def send_CMSG_NAME_QUERY(self, guid):
		"""
		Sends an unencrypted CMSG_NAME_QUERY packet.
		:return: None.
		"""
		await self._send_encrypted_packet(packets.CMSG_NAME_QUERY,
			guid=guid
		)

	async def send_CMSG_CHAR_ENUM(self):
		"""
		Sends an encrypted CMSG_CHAR_ENUM packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_CHAR_ENUM,
		)

	async def send_CMSG_PING(self, id, latency=60):
		"""
		Sends an encrypted CMSG_PING packet.
		:param id: the ping identifier (usually starts at 0 and increments)
		:param latency: the latency (in ms)
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_PING,
			id=id, latency=latency
		)

	async def send_CMSG_KEEP_ALIVE(self):
		"""
		Sends a CMSG_KEEP_ALIVE packet with optional encryption.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_KEEP_ALIVE,
		)

	async def send_CMSG_PLAYER_LOGIN(self, player_guid: Guid):
		"""
		Sends an encrypted CMSG_PLAYER_LOGIN packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_PLAYER_LOGIN,
			player_guid=player_guid
		)

	async def send_CMSG_LOGOUT_REQUEST(self):
		"""
		Sends an encrypted CMSG_LOGOUT_REQUEST packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_LOGOUT_REQUEST
		)

	async def send_CMSG_DUEL_ACCEPTED(self):
		"""
		Sends an encrypted CMSG_DUEL_ACCEPTED packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_DUEL_ACCEPTED
		)

	async def send_CMSG_GUILD_QUERY(self, guild_id: int):
		"""
		Sends an encrypted CMSG_GUILD_QUERY packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_QUERY,
			guild_id=guild_id
		)

	async def send_CMSG_GUILD_ROSTER(self):
		"""
		Sends an encrypted CMSG_GUILD_ROSTER packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_ROSTER
		)

	async def send_CMSG_GUILD_ACCEPT(self):
		"""
		Sends an encrypted CMSG_GUILD_ACCEPT packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_ACCEPT
		)

	async def send_CMSG_GUILD_SET_PUBLIC_NOTE(self, player: str, note: str):
		"""
		Sends an encrypted CMSG_GUILD_SET_PUBLIC_NOTE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_SET_PUBLIC_NOTE,
			player=player,
			note=note
		)

	async def send_CMSG_GUILD_DECLINE(self):
		"""
		Sends an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_DECLINE
		)

	async def send_CMSG_GUILD_CREATE(self, guild_name: str):
		"""
		Sends an encrypted CMSG_GUILD_CREATE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GUILD_CREATE,
			header={'size': len(guild_name) + 4},
			guild_name=guild_name
		)

	async def send_CMSG_LOGOUT_CANCEL(self):
		"""
		Sends an encrypted CMSG_LOGOUT_CANCEL packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_LOGOUT_CANCEL
		)

	async def send_CMSG_GROUP_ACCEPT(self):
		"""
		Sends an encrypted CMSG_GROUP_ACCEPT packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GROUP_ACCEPT
		)

	async def send_CMSG_GROUP_INVITE(self, invitee: str):
		"""
		Sends an encrypted CMSG_GROUP_INVITE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_GROUP_INVITE,
			header={'size': len(invitee) + 4},
			invitee=invitee,
			unknown=0,
		)

	async def send_CMSG_TIME_SYNC_RES(self, id: int, client_ticks: int):
		"""
		Sends an encrypted CMSG_TIME_SYNC_RES packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.CMSG_TIME_SYNC_RESP,
			id=id, client_ticks=(client_ticks & 0xFFFFFFFF),
		)

	async def receieve_SMSG_GROUP_INVITE(self) -> packets.SMSG_GROUP_INVITE:
		"""
		Receives an encrypted SMSG_GROUP_INVITE packet.
		:return: a parsed SMSG_GROUP_INVITE packet.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_GROUP_INVITE)

	async def receive_SMSG_ADDON_INFO(self):
		"""
		Receives an encrypted SMSG_ADDON_INFO packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_ADDON_INFO)

	async def receive_SMSG_GUILD_INVITE(self) -> packets.SMSG_GUILD_INVITE:
		"""
		Receives an encrypted SMSG_GUILD_INVITE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_GUILD_INVITE)

	async def receive_SMSG_GUILD_QUERY_RESPONSE(self) -> packets.SMSG_GUILD_QUERY_RESPONSE:
		"""
		Receives an encrypted SMSG_GUILD_QUERY_RESPONSE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_GUILD_QUERY_RESPONSE)

	async def receive_SMSG_AUTH_CHALLENGE(self) -> packets.SMSG_AUTH_CHALLENGE:
		"""
		Receives an unencrypted SMSG_AUTH_CHALLENGE packet.
		:return: a parsed SMSG_AUTH_CHALLENGE packet.
		"""
		return await self._receive_unencrypted_packet(packets.SMSG_AUTH_CHALLENGE)

	async def receive_SMSG_NAME_QUERY_RESPONSE(self, guid):
		"""
		Receives an unencrypted SMSG_NAME_QUERY_RESPONSE packet.
		:return: None.
		"""
		return await self._receive_unencrypted_packet(
			packets.SMSG_NAME_QUERY_RESPONSE
		)

	async def receive_SMSG_AUTH_RESPONSE(self) -> packets.SMSG_AUTH_RESPONSE:
		"""
		Receives an encrypted SMSG_AUTH_RESPONSE packet.
		:return: a parsed SMSG_AUTH_RESPONSE packet.
		"""
		return await self._receive_encrypted_packet(
			packets.SMSG_AUTH_RESPONSE
		)

	async def receive_SMSG_WARDEN_DATA(self) -> packets.SMSG_WARDEN_DATA:
		"""
		Receives an SMSG_WARDEN_DATA packet with optional encryption.
		:return: a parsed SMSG_WARDEN_DATA packet.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_WARDEN_DATA)

	async def receive_SMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		"""
		Receives an encrypted SMSG_CHAR_ENUM packet.
		:return: a parsed SMSG_CHAR_ENUM packet.
		"""
		return await self._receive_encrypted_packet(packets.SMSG_CHAR_ENUM)

	async def receive_SMSG_CHATMESSAGE(self) -> packets.SMSG_MESSAGECHAT:
		"""
		Receives an encrypted SMSG_CHATMESSAGE packet.
		:return: a parsed SMSG_CHATMESSAGE packet.
		"""
		return await self._receive_encrypted_packet(
			packets.SMSG_MESSAGECHAT
		)

	async def send_CMSG_MESSAGECHAT(self,
		text: str, message_type: MessageType=MessageType.say,
		language=Language.universal, recipient: Optional[str]=None,
		channel: Optional[str]=None
	):
		"""
		Sends an encrypted CMSG_MESSAGECHAT packet.
		:return: None.
		"""
		size = 4 + 4 + len(text)
		if message_type in (MessageType.whisper, MessageType.channel):
			size += max(len(channel), len(recipient))

		await self._send_encrypted_packet(
			packets.CMSG_MESSAGECHAT,
			header={'size': size + 5},
			text=text, message_type=message_type, language=language,
			receiver=recipient, channel=channel
		)

class WorldServerProtocol(WorldProtocol):
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int):
		super().__init__(stream, session_key,
            encryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
			decryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
		)

		self.parser = WorldClientPacketParser()

	def encrypt_packet(self, data: bytes, header):
		packed_header = ServerHeader().build(dict(
			opcode=header.opcode,
			size=header.size
		))

		body_start = 5 if headers.is_large_server_packet(header) else 4
		logger.debug(f'{data[:body_start]=} {packed_header=}')
		return self.encrypt(packed_header) +  data[body_start:]

	def decrypt_packet(self, data: bytes):
		# logger.debug(f'(Server) {data=}')
		if data is None or len(data) == 0:
			return None

		return self.decrypt(data[0:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self.receive_some(max_bytes=6)

		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from client')

		logger.log('PACKETS', f'(Server) Incoming packet...')
		logger.log('PACKETS', f'{original_data=}')

		try:
			header_data = self.decrypt(original_data[:6])
			header = ClientHeader().parse(header_data)
			bytes_left = header.size - 4
			logger.log('PACKETS', f'{header=}')

			if bytes_left > 0:
				logger.log('PACKETS', f'Listening for {bytes_left} byte body...')
				body = await self.receive_some(max_bytes=bytes_left)
				data = header_data + body
				# logger.log('PACKETS', f'{data=}')

				if data is None or len(data) == 0:
					raise ProtocolError('received EOF from server')
			else:
				data = header

			try:
				packet = self.parser.parse(data, header)
				self._num_packets_received += 1
				return packet

			except (KeyError, ConstructError) as e:
				if type(e) is KeyError:
					logger.log('PACKETS', f'Dropped packet: {header=}')
				else:
					traceback.print_exc()

		except ValueError as e:
			if 'is not a valid Opcode' in str(e):
				raise ProtocolError('Invalid opcode, stream might be out of sync')

	async def send_SMSG_AUTH_RESPONSE(self,
		response: AuthResponse, expansion=Expansion.wotlk,
		queue_position: Optional[int] = None,
		billing=None
	):
		"""
		Sends an encrypted SMSG_AUTH_RESPONSE packet.
		:return: None.
		"""
		if billing is None:
			billing = dict(billing=dict(
				time_left=0, time_rested=0,
				plan=0,
			))

		size = 1 + (4 + 1 + 4) + 1
		if queue_position is not None:
			size += 4

		await self._send_encrypted_packet(
			packets.SMSG_AUTH_RESPONSE,
			header=dict(size=size + 2),
			response=response, expansion=expansion,
			queue_position=queue_position,
			billing=billing,
		)

	async def send_SMSG_AUTH_CHALLENGE(self, server_seed: int = random.getrandbits(32),
	                                   encryption_seed1: int = random.getrandbits(16),
	                                   encryption_seed2: int = random.getrandbits(16)):
		"""
		Sends an unencrypted SMSG_AUTH_CHALLENGE packet.
		:param server_seed:
		:param encryption_seed1:
		:param encryption_seed2:
		:return: None.
		"""
		await self._send_unencrypted_packet(
			packets.SMSG_AUTH_CHALLENGE,
			server_seed=server_seed,
			encryption_seed1=encryption_seed1,
			encryption_seed2=encryption_seed2
		)

	async def send_SMSG_NAME_QUERY_RESPONSE(self, guid, found: bool, info):
		"""
		Sends an unencrypted SMSG_NAME_QUERY_RESPONSE packet.
		:return: None.
		"""
		info_size = len(info['name']) + 1 + len(info['realm_name']) + 1 + 4
		guid_size = compute_packed_guid_byte_size(pack_guid(guid)[0])

		await self._send_encrypted_packet(
			packets.SMSG_NAME_QUERY_RESPONSE,
			header={'size': 2 + guid_size + 2 + info_size},
			guid=Guid(guid), found=found, info=info
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
		raise NotImplemented()
		# await self._send_encrypted_packet(
		# 	'SMSG_WARDEN_DATA', packets.SMSG_WARDEN_DATA,
		# 	command=command,
		# 	module_id=module_id,
		# 	module_key=module_key,
		# 	size=size
		# )

	async def send_SMSG_CHAR_ENUM(self):
		"""
		Sends an encrypted SMSG_CHAR_ENUM packet.
		:return: None.
		"""
		await self._send_encrypted_packet(packets.SMSG_CHAR_ENUM)

	async def send_SMSG_ADDON_INFO(self, data: bytes):
		"""
		Sends an encrypted SMSG_ADDON_INFO packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.SMSG_ADDON_INFO,
			header={'size': len(data) + 2},
			data=data,
		)

	async def send_SMSG_GUILD_QUERY_RESPONSE(self,
		guild_id: int,
		name: str,
		ranks: List[str],
		emblem_style: int,
		emblem_color: int,
		border_style: int,
		border_color: int,
		background_color: int,
		num_ranks: int,
	):
		"""
		Sends an encrypted SMSG_GUILD_QUERY_RESPONSE packet.
		:return: None.
		"""
		ranks_size = sum((len(s) + 1 for s in ranks))
		await self._send_encrypted_packet(
			packets.SMSG_GUILD_QUERY_RESPONSE,
			header={'size': 4 + len(name) + 1 + ranks_size + 4 * 6},
			guild_id=guild_id,
			name=name,
			ranks=ranks,
			emblem_style=emblem_style,
			emblem_color=emblem_color,
			border_style=border_style,
			border_color=border_color,
			background_color=background_color,
			num_ranks=num_ranks,
		)

	async def send_SMSG_GUILD_INVITE(self, inviter: str, guild: str):
		"""
		Sends an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.SMSG_GUILD_INVITE,
			header={'size': len(inviter) + len(guild) + 2},
			inviter=inviter,
			guild=guild
		)

	async def send_SMSG_GROUP_INVITE(self, inviter: str, in_group=False):
		"""
		Sends an encrypted SMSG_GROUP_INVITE packet.
		:return: None.
		"""
		await self._send_encrypted_packet(
			packets.SMSG_GROUP_INVITE,
			header={'size': 1 + len(inviter) + 4 + 1 + 4},
			in_group=in_group,
			inviter=inviter
		)

	async def receieve_CMSG_MESSAGECHAT(self):
		"""
		Sends an encrypted CMSG_MESSAGECHAT packet.
		:return: None.
		"""
		await self._receive_encrypted_packet(
			packets.CMSG_MESSAGECHAT,
		)

	async def receive_CMSG_AUTH_SESSION(self) -> packets.CMSG_AUTH_SESSION:
		"""
		Receives an unencrypted CMSG_AUTH_SESSION packet.
		:return: a parsed CMSG_AUTH_SESSION packet.
		"""
		return await self._receive_unencrypted_packet(
			packets.CMSG_AUTH_SESSION
		)

	async def receive_CMSG_NAME_QUERY(self, guid):
		"""
		Receives an unencrypted CMSG_NAME_QUERY packet.
		:return: None.
		"""
		return await self._receive_unencrypted_packet(
			packets.CMSG_NAME_QUERY
		)

	async def receive_CMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		"""
		Receives an encrypted CMSG_CHAR_ENUM packet.
		:return: a parsed CMSG_CHAR_ENUM packet.
		"""
		return await self._receive_encrypted_packet(packets.CMSG_CHAR_ENUM)


	async def receive_CMSG_PING(self) -> packets.CMSG_PING:
		"""
		Receives an encrypted CMSG_PING packet.
		:return: a parsed CMSG_PING packet.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_PING,
		)

	async def receive_CMSG_KEEP_ALIVE(self):
		"""
		Receives and decrypts (if necessary) a CMSG_KEEP_ALIVE packet.
		:return: a parsed CMSG_KEEP_ALIVE packet.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_KEEP_ALIVE,
		)

	async def receive_CMSG_PLAYER_LOGIN(self):
		"""
		Receives an encrypted CMSG_PLAYER_LOGIN packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_PLAYER_LOGIN
		)

	async def receive_CMSG_LOGOUT_REQUEST(self):
		"""
		Receives an encrypted CMSG_LOGOUT_REQUEST packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_LOGOUT_REQUEST
		)

	async def receive_CMSG_DUEL_ACCEPTED(self) -> packets.CMSG_DUEL_ACCEPTED:
		"""
		Receives an encrypted CMSG_DUEL_ACCEPTED packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_DUEL_ACCEPTED
		)

	async def receive_CMSG_GUILD_QUERY(self) -> packets.CMSG_GUILD_QUERY:
		"""
		Receives an encrypted CMSG_GUILD_QUERY packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_GUILD_QUERY,
		)


	async def receive_CMSG_GUILD_ROSTER(self) -> packets.CMSG_GUILD_ROSTER:
		"""
		Receives an encrypted CMSG_GUILD_ROSTER packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_GUILD_ROSTER
		)

	async def receive_CMSG_GUILD_ACCEPT(self) -> packets.CMSG_GUILD_ACCEPT:
		"""
		Receives an encrypted CMSG_GUILD_ACCEPT packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_GUILD_ACCEPT
		)

	async def receive_CMSG_GUILD_SET_PUBLIC_NOTE(self) -> packets.CMSG_GUILD_SET_PUBLIC_NOTE:
		"""
		Receives an encrypted CMSG_GUILD_SET_PUBLIC_NOTE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(packets.CMSG_GUILD_SET_PUBLIC_NOTE)


	async def receive_CMSG_GUILD_DECLINE(self) -> packets.CMSG_GUILD_DECLINE:
		"""
		Receives an encrypted CMSG_GUILD_DECLINE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(packets.CMSG_GUILD_DECLINE)

	async def receive_CMSG_GUILD_CREATE(self) -> packets.CMSG_GUILD_CREATE:
		"""
		Receives an encrypted CMSG_GUILD_CREATE packet.
		:return: None.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_GUILD_CREATE
		)

	async def receive_CMSG_LOGOUT_CANCEL(self) -> packets.CMSG_LOGOUT_CANCEL:
		"""
		Receives an encrypted CMSG_LOGOUT_CANCEL packet.
		:return: a parsed CMSG_LOGOUT_CANCEL packet.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_LOGOUT_CANCEL
		)

	async def receive_CMSG_GROUP_INVITE(self) -> packets.CMSG_GROUP_INVITE:
		"""
		Receives an encrypted CMSG_GROUP_INVITE packet.
		:return: a parsed CMSG_GROUP_INVITE packet.
		"""
		return await self._receive_encrypted_packet(
			'CMSG_GROUP_INVITE',
			packets.CMSG_GROUP_INVITE
		)

	async def receive_CMSG_TIME_SYNC_RES(self) -> packets.CMSG_TIME_SYNC_RESP:
		"""
		Receives an encrypted CMSG_TIME_SYNC_RES packet.
		:return: a parsed CMSG_TIME_SYNC_RES packet.
		"""
		return await self._receive_encrypted_packet(
			packets.CMSG_TIME_SYNC_RESP,
		)