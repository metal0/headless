from typing import Dict, Optional

import construct
from construct import ConstructError

from .addon_info import SMSG_ADDON_INFO
from .auth_packets import SMSG_AUTH_RESPONSE, SMSG_AUTH_CHALLENGE
from .bind_point import SMSG_BIND_POINT_UPDATE
from .char_enum import SMSG_CHAR_ENUM
from .chat_packets import SMSG_MESSAGECHAT, SMSG_GM_MESSAGECHAT
from .clientcache_version import SMSG_CLIENTCACHE_VERSION
from ..opcode import Opcode
from .guild_packets import SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_ROSTER, SMSG_GUILD_INVITE, SMSG_GUILD_EVENT
from .headers import ServerHeader
from .login_packets import SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_COMPLETE
from .motd import SMSG_MOTD
from .name_query import SMSG_NAME_QUERY_RESPONSE
from .ping import SMSG_PONG
from .query_time import SMSG_QUERY_TIME_RESPONSE
from .time_sync import SMSG_TIME_SYNC_REQ
from .tutorial_flags import SMSG_TUTORIAL_FLAGS
from .warden_packets import SMSG_WARDEN_DATA
from .world_states import SMSG_INIT_WORLD_STATES
from .... import log

log = log.mgr.get_logger(__name__)

class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}
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

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse_header(self, data: bytes) -> ServerHeader:
		try:
			return ServerHeader().parse(data)
		except ConstructError:
			return None

	def parse(self, data: bytes):
		header = ServerHeader().parse(data)
		return self._parsers[header.opcode].parse(data)

parser = WorldPacketParser()