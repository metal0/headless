import construct

from pont.utility.construct import GuidConstruct, PackedGuid, PackEnum
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...entities.player import Race, Gender, CombatClass
from ...guid import Guid

CMSG_NAME_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_NAME_QUERY, 8),
	'guid' / construct.ByteSwapped(GuidConstruct(Guid))
)

NameInfo = construct.Struct(
	'name' / construct.CString('ascii'),
	'realm_name' / construct.Default(construct.CString('ascii'), ''),
	'race' / PackEnum(Race),
	'gender' / PackEnum(Gender),
	'combat_class' / PackEnum(CombatClass),
)

SMSG_NAME_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_NAME_QUERY_RESPONSE, 8+1+1+1+1+1+10),
	'guid' / PackedGuid(Guid),
	'name_unknown' / construct.Default(construct.Flag, False),
	'info' / construct.If(not construct.this.name_unknown, NameInfo)
)
