import construct

from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ClientHeader, ServerHeader

CMSG_PING = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PING, 8),
	'id' / construct.Default(construct.Int32ul, 0),
	'latency' / construct.Default(construct.Int32ul, 60),
)

SMSG_PONG = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_PONG, 4),
	'ping' / construct.Int32ul,
)
