import construct

from pont.utility.construct import GuidConstruct, PackedGuid
from .constants.opcode import Opcode
from .headers import ServerHeader, ClientHeader
from ...guid import Guid

CMSG_NAME_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_NAME_QUERY, 8),
	'guid' / construct.ByteSwapped(GuidConstruct(Guid))
)

SMSG_NAME_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_NAME_QUERY_RESPONSE, 8+1+1+1+1+1+10),
	'guid' / PackedGuid(Guid),
	'name_known' / construct.Default(construct.Flag, 1),
	'name' / construct.CString('ascii'),
	'realm_name' / construct.Default(construct.CString('ascii'), ''),
	# 'race' / PackEnum(Race),
	# 'gender' / PackEnum(Gender),
	# 'combat_class' / PackEnum(CombatClass),
)
