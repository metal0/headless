import construct

from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...character import CharacterInfo

CMSG_CHAR_ENUM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_ENUM, 0),
)

SMSG_CHAR_ENUM = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_ENUM, 4 + construct.len_(construct.this.characters)),
	'characters' / construct.PrefixedArray(construct.Byte, CharacterInfo),
)
