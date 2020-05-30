import construct
from .constants import Opcode, opcodes
from ..realm import Realm
from pont.client.auth.packets.parse import parser

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.realm_list, Opcode), opcodes.realm_list),
	'packet_size' / construct.ByteSwapped(construct.Short),
	construct.Padding(4),
	'num_realms' / construct.ByteSwapped(construct.Short),
	'realms' / Realm[construct.this.num_realms],
)

parser.set_parser(opcode=opcodes.realm_list, parser=RealmlistResponse)