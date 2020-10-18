import construct

from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode

CMSG_TIME_SYNC_RESP = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_TIME_SYNC_RESP, 8),
	'id' / construct.Int32ul,
	'client_ticks' / construct.Int32ul,
)

SMSG_TIME_SYNC_REQ = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TIME_SYNC_REQ, 4),
	'id' / construct.Int32ul,
)
