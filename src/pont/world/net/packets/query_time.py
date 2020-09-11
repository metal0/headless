import construct

from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode

CMSG_QUERY_TIME = construct.Struct(
	'header' / ClientHeader(Opcode.SMSG_QUERY_TIME_RESPONSE, 0),
)

SMSG_QUERY_TIME_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_QUERY_TIME_RESPONSE, 8),
	'game_time' / construct.Int32ul,
	'time_until_reset' / construct.Int32ul
)
