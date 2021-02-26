import construct

from .headers import ServerHeader
from ..opcode import Opcode

SMSG_TUTORIAL_FLAGS = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TUTORIAL_FLAGS, 4 * 8),
	'tutorials' / construct.ByteSwapped(construct.Array(8, construct.Int))
)
