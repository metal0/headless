from enum import Enum

import construct

from pont.utility.construct import PackEnum
from .headers import ServerHeader
from ..opcode import Opcode

class ServerMessageType(Enum):
	shutdown_time = 1
	restart_time = 2
	custom = 3
	shutdown_cancelled = 4
	restart_cancelled = 5

SMSG_SERVER_MESSAGE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_SERVER_MESSAGE, 50),
	'type' / PackEnum(ServerMessageType),
	'text' / construct.CString('ascii')
)

SMSG_NOTIFICATION = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_NOTIFICATION, 1),
	'message' / construct.CString('ascii')
)

SMSG_MOTD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MOTD, 4),
	'lines' / construct.PrefixedArray(construct.Int32ul, construct.CString('ascii'))
)