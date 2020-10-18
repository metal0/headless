import construct

from pont.utility.construct import Coordinates, GuidConstruct
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...guid import Guid

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGIN_VERIFY_WORLD, 20),
	'map' / construct.Int32ul,
	'position' / construct.ByteSwapped(Coordinates()),
	'rotation' / construct.Float32l,
)

SMSG_LOGOUT_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_RESPONSE, 5),
	'reason' / construct.Int32ul,
	'instant_logout' / construct.Flag,
)

SMSG_LOGOUT_CANCEL_ACK = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_CANCEL_ACK, 0),
)

SMSG_LOGOUT_COMPLETE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_COMPLETE, 0),
)

CMSG_PLAYER_LOGIN = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PLAYER_LOGIN, 8),
	'player_guid' / GuidConstruct(Guid)
)

CMSG_LOGOUT_REQUEST = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_LOGOUT_REQUEST, 0),
)

CMSG_LOGOUT_CANCEL = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_LOGOUT_CANCEL, 0),
)