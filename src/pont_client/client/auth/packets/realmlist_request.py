import construct

from pont_client.utility.construct import ConstructEnum
from .constants import opcodes, Opcode

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.realm_list, ConstructEnum(Opcode)), opcodes.realm_list),
	construct.Padding(4)
)
