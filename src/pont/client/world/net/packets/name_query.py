import construct

from ...entities.player import CombatClass, Gender, Race
from .parse import parser
from .constants.opcode import Opcode
from .headers import ServerHeader, ClientHeader
from pont.utility.construct import PackEnum, GuidConstruct
from ...guid import Guid

CMSG_NAME_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_NAME_QUERY, 8),
	'guid' / construct.ByteSwapped(GuidConstruct(Guid))
)

SMSG_NAME_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_NAME_QUERY_RESPONSE, 8),
	'guid' / construct.Byte,
	'name_known' / construct.Default(construct.Flag, 1),
	'name' / construct.CString('ascii'),
	'realm_name' / construct.CString('ascii'),
	'race' / PackEnum(Race),
	'gender' / PackEnum(Gender),
	'combat_class' / PackEnum(CombatClass),
)

parser.set_parser(Opcode.SMSG_NAME_QUERY_RESPONSE, SMSG_NAME_QUERY_RESPONSE)