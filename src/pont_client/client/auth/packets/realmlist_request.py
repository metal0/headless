import construct
from .constants import opcodes, Opcode

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.realm_list, Opcode), opcodes.realm_list),
	construct.Padding(4)
)
