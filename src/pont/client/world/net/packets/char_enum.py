import construct

from .parse import parser
from .constants import Opcode
from .headers import ClientHeader, ServerHeader
from ...character_select import CharacterInfo

CMSG_CHAR_ENUM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_ENUM, 0),
)

SMSG_CHAR_ENUM = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_ENUM, 4 + construct.len_(construct.this.characters)),
	'characters' / construct.PrefixedArray(construct.Byte, CharacterInfo),
)

parser.set_parser(Opcode.SMSG_CHAR_ENUM, SMSG_CHAR_ENUM)