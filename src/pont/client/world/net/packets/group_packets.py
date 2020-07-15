import construct

from ..opcode import Opcode
from .headers import ClientHeader, ServerHeader

CMSG_GROUP_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_INVITE, 10),
	'invitee' / construct.CString('ascii'),
	'unknown' / construct.Default(construct.Int32ul, 0)
)

CMSG_GROUP_ACCEPT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_ACCEPT, 4),
	'unknown' / construct.Default(construct.Int32ul, 0),
)

SMSG_GROUP_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_INVITE, 10),
	'in_group' / construct.Flag,
	'inviter' / construct.CString('ascii'),
	'unknown1' / construct.Default(construct.Int32ul, 0),
	'count' / construct.Default(construct.Byte, 0),
	'unknown2' / construct.Default(construct.Int32ul, 0)
)