import construct

from pont_client.utility.construct import ConstructEnum
from .parse import parser
from .constants import Opcode, opcodes
from ..realm import Realm

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.realm_list, ConstructEnum(Opcode)), opcodes.realm_list),
	'packet_size' / construct.ByteSwapped(construct.Short),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.ByteSwapped(construct.Short), Realm),
)

parser.set_parser(opcode=opcodes.realm_list, parser=RealmlistResponse)