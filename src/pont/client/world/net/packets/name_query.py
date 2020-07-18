import construct

from pont.utility.construct import GuidConstruct, PackedGuid, PackEnum
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...entities.player import Race, Gender, CombatClass
from ...guid import Guid

CMSG_NAME_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_NAME_QUERY, 8),
	'guid' / GuidConstruct(Guid)
)

NameInfo = construct.Struct(
	'name' / construct.CString('utf-8'),
	# 'realm_name' / construct.Default(construct.CString('utf-8'), ''),
	# 'race' / PackEnum(Race),
	# 'gender' / PackEnum(Gender),
	# 'combat_class' / PackEnum(CombatClass),
	# 'declined' / construct.Default(construct.Flag, False)
)

SMSG_NAME_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_NAME_QUERY_RESPONSE, 8+1+1+1+1+1+10),
	'guid' / PackedGuid(Guid),
	'found' / construct.Default(construct.Flag, False),
	'info' / construct.If(construct.this.found, NameInfo)
)
