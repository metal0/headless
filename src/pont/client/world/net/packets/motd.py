import construct

from ..opcode import Opcode
from .headers import ServerHeader

SMSG_MOTD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MOTD, 4),
	'lines' / construct.PrefixedArray(construct.Int32ul, construct.CString('ascii'))
)
