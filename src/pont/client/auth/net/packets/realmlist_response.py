import construct

from pont.client.auth.realm import Realm
from pont.utility.construct import PackEnum
from .constants import Opcode

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'packet_size' / construct.Default(construct.ByteSwapped(construct.Short),  7 + construct.len_(construct.this.realms)),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.ByteSwapped(construct.Short), Realm),
)
