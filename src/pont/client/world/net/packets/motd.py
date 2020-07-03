import construct

from .constants import Opcode
from .headers import ServerHeader
from .parse import parser

SMSG_MOTD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MOTD, 4),
	'lines' / construct.PrefixedArray(construct.Int32ul, construct.CString('ascii'))
)

parser.set_parser(Opcode.SMSG_MOTD, SMSG_MOTD)