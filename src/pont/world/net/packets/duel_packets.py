import construct

from pont.utility.construct import GuidConstruct
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...guid import Guid

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
	'flag_obj' / GuidConstruct(Guid),
	'requester' / GuidConstruct(Guid),
)
