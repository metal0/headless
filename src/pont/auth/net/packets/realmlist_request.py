import construct

from pont.utility.construct import PackEnum
from ..opcode import Opcode

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	construct.Padding(4)
)
