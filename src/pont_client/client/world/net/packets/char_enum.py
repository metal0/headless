import construct

from .constants import Opcode
from pont_client.utility.construct import ConstructEnum

SMSG_CHAR_ENUM = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.SMSG_CHAR_ENUM, ConstructEnum(Opcode)), Opcode.SMSG_CHAR_ENUM),
)


