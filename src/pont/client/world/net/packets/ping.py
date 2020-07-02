import construct

from pont.client.world.net.packets.headers import ClientHeader, ServerHeader
from pont.client.world.net.packets.parse import parser
from pont.client.world.net.packets.constants import Opcode

CMSG_PING = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PING, 8),
	'id' / construct.Default(construct.ByteSwapped(construct.Int), 0),
	'latency' / construct.Default(construct.ByteSwapped(construct.Int), 60),
)

SMSG_PONG = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_PONG, 4),
	'ping' / construct.Int,
)

parser.set_parser(Opcode.SMSG_PONG, SMSG_PONG)
