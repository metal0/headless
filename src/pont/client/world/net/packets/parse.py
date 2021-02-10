
import construct
from construct import ConstructError
from typing import Dict, Optional

from pont.utility.construct import int8
from .addon_info import SMSG_ADDON_INFO
from .auth_packets import SMSG_AUTH_RESPONSE, SMSG_AUTH_CHALLENGE
from .bind_point import SMSG_BIND_POINT_UPDATE
from .char_enum import SMSG_CHAR_ENUM
from .chat_packets import SMSG_MESSAGECHAT, SMSG_GM_MESSAGECHAT
from .clientcache_version import SMSG_CLIENTCACHE_VERSION
from .duel_packets import SMSG_DUEL_REQUESTED
from .faction_packets import SMSG_INITIALIZE_FACTIONS
from .group_packets import SMSG_GROUP_INVITE
from .guild_packets import SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_ROSTER, SMSG_GUILD_INVITE, SMSG_GUILD_EVENT
from .headers import ServerHeader, ClientHeader, parse_server_header, parse_client_header
from .login_packets import SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_COMPLETE, SMSG_LOGIN_VERIFY_WORLD
from .misc_packets import SMSG_INIT_WORLD_STATES
from .motd import SMSG_MOTD
from .name_query import SMSG_NAME_QUERY_RESPONSE
from .ping import SMSG_PONG, CMSG_PING
from .query_time import SMSG_QUERY_TIME_RESPONSE
from .server_message import SMSG_SERVER_MESSAGE, SMSG_NOTIFICATION
from .time_sync import SMSG_TIME_SYNC_REQ
from .tutorial_flags import SMSG_TUTORIAL_FLAGS
from .update_packets import SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_UPDATE_OBJECT
from .warden_packets import SMSG_WARDEN_DATA
from ..opcode import Opcode
from ....log import logger


class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse_header(self, data: bytes) -> ServerHeader:
		raise NotImplemented()

	def parse(self, data: bytes, header):
		raise NotImplemented

class WorldServerPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		self.set_parser(Opcode.SMSG_ADDON_INFO, SMSG_ADDON_INFO)
		self.set_parser(Opcode.SMSG_AUTH_RESPONSE, SMSG_AUTH_RESPONSE)
		self.set_parser(Opcode.SMSG_AUTH_CHALLENGE, SMSG_AUTH_CHALLENGE)
		self.set_parser(Opcode.SMSG_BIND_POINT_UPDATE, SMSG_BIND_POINT_UPDATE)
		self.set_parser(Opcode.SMSG_CHAR_ENUM, SMSG_CHAR_ENUM)
		self.set_parser(Opcode.SMSG_CLIENTCACHE_VERSION, SMSG_CLIENTCACHE_VERSION)
		self.set_parser(Opcode.SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_QUERY_RESPONSE)
		self.set_parser(Opcode.SMSG_GUILD_ROSTER, SMSG_GUILD_ROSTER)
		self.set_parser(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE)
		self.set_parser(Opcode.SMSG_GUILD_EVENT, SMSG_GUILD_EVENT)
		self.set_parser(Opcode.SMSG_TIME_SYNC_REQ, SMSG_TIME_SYNC_REQ)
		self.set_parser(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT)
		self.set_parser(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT)
		self.set_parser(Opcode.SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGIN_VERIFY_WORLD)
		self.set_parser(Opcode.SMSG_MOTD, SMSG_MOTD)
		self.set_parser(Opcode.SMSG_NAME_QUERY_RESPONSE, SMSG_NAME_QUERY_RESPONSE)
		self.set_parser(Opcode.SMSG_PONG, SMSG_PONG)
		self.set_parser(Opcode.SMSG_QUERY_TIME_RESPONSE, SMSG_QUERY_TIME_RESPONSE)
		self.set_parser(Opcode.SMSG_TUTORIAL_FLAGS, SMSG_TUTORIAL_FLAGS)
		self.set_parser(Opcode.SMSG_WARDEN_DATA, SMSG_WARDEN_DATA)
		self.set_parser(Opcode.SMSG_INIT_WORLD_STATES, SMSG_INIT_WORLD_STATES)
		self.set_parser(Opcode.SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_RESPONSE)
		self.set_parser(Opcode.SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_CANCEL_ACK)
		self.set_parser(Opcode.SMSG_LOGOUT_COMPLETE, SMSG_LOGOUT_COMPLETE)
		self.set_parser(Opcode.SMSG_GROUP_INVITE, SMSG_GROUP_INVITE)
		self.set_parser(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE)
		self.set_parser(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT)
		self.set_parser(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT)
		self.set_parser(Opcode.SMSG_SERVER_MESSAGE, SMSG_SERVER_MESSAGE)
		self.set_parser(Opcode.SMSG_NOTIFICATION, SMSG_NOTIFICATION)
		self.set_parser(Opcode.SMSG_DUEL_REQUESTED, SMSG_DUEL_REQUESTED)
		self.set_parser(Opcode.SMSG_UPDATE_OBJECT, SMSG_UPDATE_OBJECT)
		self.set_parser(Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_COMPRESSED_UPDATE_OBJECT)

	def parse_header(self, data: bytes) -> ServerHeader:
		try:
			return parse_server_header(data)
		except ConstructError:
			return None

	def parse(self, data: bytes, header, large=False):
		header = parse_server_header(data)
		body_start = 5 if large else 4
		return self._parsers[header.opcode].parse(ServerHeader().build(header) + data[body_start:])

class WorldClientPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		self.set_parser(Opcode.CMSG_PING, CMSG_PING)

	def parse_header(self, data: bytes) -> ServerHeader:
		try:
			return parse_client_header(data)
		except ConstructError:
			return None

	def parse(self, data: bytes, header, large=False):
		return self._parsers[header.opcode].parse(data)
