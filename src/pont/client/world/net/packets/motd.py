import construct

from .headers import ServerHeader
from ..opcode import Opcode

SMSG_MOTD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MOTD, 4),
	'lines' / construct.PrefixedArray(construct.Int32ul, construct.CString('ascii'))
)
