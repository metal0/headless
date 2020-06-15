import construct

from pont_client.client.auth.realm import Realm
from pont_client.utility.construct import PackEnum
from .parse import parser
from .constants import Opcode

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'packet_size' / construct.Default(construct.ByteSwapped(construct.Short),  7 + construct.len_(construct.this.realms)),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.ByteSwapped(construct.Short), Realm),
)

parser.set_parser(opcode=Opcode.realm_list, parser=RealmlistResponse)