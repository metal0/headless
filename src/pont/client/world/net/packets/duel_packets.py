import construct

from ...guid import Guid
from ..opcode import Opcode
from .headers import ServerHeader, ClientHeader
from pont.utility.construct import GuidConstruct

CMSG_DUEL_ACCEPTED = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_DUEL_ACCEPTED, 8),
	'unk' / construct.Default(GuidConstruct(Guid), Guid()),
)

CMSG_DUEL_CANCELLED = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_DUEL_CANCELLED, 8),
	'unk' / GuidConstruct(Guid),
)

SMSG_DUEL_REQUESTED = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_DUEL_REQUESTED, 8 + 8),
	'duel_flag' / GuidConstruct(Guid),
	'requester' / GuidConstruct(Guid),
)

