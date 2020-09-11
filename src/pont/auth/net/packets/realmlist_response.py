import construct

from pont.auth.realm import Realm
from pont.utility.construct import PackEnum
from ..opcode import Opcode

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'packet_size' / construct.Default(construct.Int16ul,  8 + construct.len_(construct.this.realms)),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.Int16ul, Realm),
	# construct.Default(construct.Array(2, construct.Byte), [16, 0])
)
