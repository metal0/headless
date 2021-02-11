import construct

from pont.client.auth.realm import Realm
from pont.utility.construct import PackEnum
from ..opcode import Opcode

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'size' / construct.Default(construct.Int16ul,  8),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.Int16ul, Realm),
)
