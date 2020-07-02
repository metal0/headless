import construct

from .parse import parser
from .constants import Opcode
from .headers import ServerHeader, ClientHeader

CMSG_TIME_SYNC_RES = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_TIME_SYNC_RESP, 4),
	'id' / construct.ByteSwapped(construct.Int)
)

#
# # TODO: SMSG_TIME_SYNC_REQ
# SMSG_TIME_SYNC_REQ = construct.Struct(
# 	'header' / ServerHeader(Opcode.SMSG_TIME_SYNC_REQ, 4),
# 	''
# )
#
# parser.set_parser(Opcode.SMSG_TIME_SYNC_REQ, SMSG_TIME_SYNC_REQ)