
import construct
from construct import ConstructError
from typing import Dict, Optional

from pont.utility.construct import int8
from . import SMSG_WHOIS, SMSG_MOTD, SMSG_WHO
from .auction_packets import CMSG_AUCTION_SELL_ITEM, CMSG_AUCTION_PLACE_BID, CMSG_AUCTION_LIST_ITEMS, \
	CMSG_AUCTION_LIST_PENDING_SALES, CMSG_AUCTION_LIST_OWNER_ITEMS, MSG_AUCTION_HELLO, SMSG_AUCTION_LIST_RESULT
from .auth_packets import SMSG_AUTH_RESPONSE, SMSG_AUTH_CHALLENGE
from .bind_point import SMSG_BIND_POINT_UPDATE
from .char_enum import SMSG_CHAR_ENUM
from .chat_packets import SMSG_MESSAGECHAT, SMSG_GM_MESSAGECHAT
from .duel_packets import SMSG_DUEL_REQUESTED
from .group_packets import SMSG_GROUP_INVITE
from .guild_packets import SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_ROSTER, SMSG_GUILD_INVITE, SMSG_GUILD_EVENT
from .headers import ServerHeader, ClientHeader
from .login_packets import SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_COMPLETE, SMSG_LOGIN_VERIFY_WORLD
from .mail_packets import CMSG_GET_MAIL_LIST, SMSG_MAIL_LIST_RESULT
from .misc_packets import SMSG_CLIENTCACHE_VERSION, SMSG_INIT_WORLD_STATES, SMSG_ADDON_INFO
from .name_query import SMSG_NAME_QUERY_RESPONSE
from .ping import SMSG_PONG, CMSG_PING
from .server_message import SMSG_SERVER_MESSAGE, SMSG_NOTIFICATION
from .time_packets import SMSG_TIME_SYNC_REQ, CMSG_QUERY_TIME, SMSG_QUERY_TIME_RESPONSE
from .tutorial_flags import SMSG_TUTORIAL_FLAGS
from .update_packets import SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_UPDATE_OBJECT
from .warden_packets import SMSG_WARDEN_DATA
from ..opcode import Opcode


class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse_header(self, data: bytes) -> ServerHeader:
		raise NotImplemented()

	def parse(self, data: bytes, header):
		raise NotImplemented

	def parser(self, opcode):
		return self._parsers[opcode]

class WorldServerPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		parsers = [
			(Opcode.SMSG_ADDON_INFO, SMSG_ADDON_INFO),
			(Opcode.SMSG_AUTH_RESPONSE, SMSG_AUTH_RESPONSE),
			(Opcode.SMSG_AUTH_CHALLENGE, SMSG_AUTH_CHALLENGE),
			(Opcode.SMSG_BIND_POINT_UPDATE, SMSG_BIND_POINT_UPDATE),
			(Opcode.SMSG_CHAR_ENUM, SMSG_CHAR_ENUM),
			(Opcode.SMSG_CLIENTCACHE_VERSION, SMSG_CLIENTCACHE_VERSION),
			(Opcode.SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_QUERY_RESPONSE),
			(Opcode.SMSG_GUILD_ROSTER, SMSG_GUILD_ROSTER),
			(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE),
			(Opcode.SMSG_GUILD_EVENT, SMSG_GUILD_EVENT),
			(Opcode.SMSG_TIME_SYNC_REQ, SMSG_TIME_SYNC_REQ),
			(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT),
			(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT),
			(Opcode.SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGIN_VERIFY_WORLD),
			(Opcode.SMSG_MOTD, SMSG_MOTD),
			(Opcode.SMSG_NAME_QUERY_RESPONSE, SMSG_NAME_QUERY_RESPONSE),
			(Opcode.SMSG_PONG, SMSG_PONG),
			(Opcode.SMSG_QUERY_TIME_RESPONSE, SMSG_QUERY_TIME_RESPONSE),
			(Opcode.SMSG_TUTORIAL_FLAGS, SMSG_TUTORIAL_FLAGS),
			(Opcode.SMSG_WARDEN_DATA, SMSG_WARDEN_DATA),
			(Opcode.SMSG_INIT_WORLD_STATES, SMSG_INIT_WORLD_STATES),
			(Opcode.SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_RESPONSE),
			(Opcode.SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_CANCEL_ACK),
			(Opcode.SMSG_LOGOUT_COMPLETE, SMSG_LOGOUT_COMPLETE),
			(Opcode.SMSG_GROUP_INVITE, SMSG_GROUP_INVITE),
			(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE),
			(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT),
			(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT),
			(Opcode.SMSG_SERVER_MESSAGE, SMSG_SERVER_MESSAGE),
			(Opcode.SMSG_NOTIFICATION, SMSG_NOTIFICATION),
			(Opcode.SMSG_DUEL_REQUESTED, SMSG_DUEL_REQUESTED),
			(Opcode.SMSG_UPDATE_OBJECT, SMSG_UPDATE_OBJECT),
			(Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_COMPRESSED_UPDATE_OBJECT),
			(Opcode.SMSG_MAIL_LIST_RESULT, SMSG_MAIL_LIST_RESULT),
			(Opcode.SMSG_WHOIS, SMSG_WHOIS),
			(Opcode.SMSG_AUCTION_LIST_RESULT, SMSG_AUCTION_LIST_RESULT),
			(Opcode.SMSG_WHO, SMSG_WHO),
		]

		for opcode, parser in parsers:
			self.set_parser(opcode, parser)

	def parse(self, data: bytes, header):
		return self._parsers[header.opcode].parse(data)

class WorldClientPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		parsers = [
			(Opcode.CMSG_PING, CMSG_PING),
			(Opcode.CMSG_GET_MAIL_LIST, CMSG_GET_MAIL_LIST),
			# (Opcode.CMSG_SEND_MAIL, CMSG_SEND_MAIL),
			(Opcode.MSG_AUCTION_HELLO, MSG_AUCTION_HELLO(server=False)),
			# (Opcode.CMSG_AUCTION_LIST_BIDDER_ITEMS, CMSG_AUCTION_LIST_BIDDER_ITEMS),
			(Opcode.CMSG_AUCTION_LIST_OWNER_ITEMS, CMSG_AUCTION_LIST_OWNER_ITEMS),
			(Opcode.CMSG_AUCTION_LIST_PENDING_SALES, CMSG_AUCTION_LIST_PENDING_SALES),
			(Opcode.CMSG_AUCTION_LIST_ITEMS, CMSG_AUCTION_LIST_ITEMS),
			(Opcode.CMSG_AUCTION_PLACE_BID, CMSG_AUCTION_PLACE_BID),
			(Opcode.CMSG_AUCTION_SELL_ITEM, CMSG_AUCTION_SELL_ITEM),
		]

		for opcode, parser in parsers:
			self.set_parser(opcode, parser)

	def parse(self, data: bytes, header, large=False):
		return self._parsers[header.opcode].parse(data)
