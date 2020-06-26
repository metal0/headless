import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.client.world.net.packets.headers import ClientHeader

CMSG_PING = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PING, 8),
	'unk' / construct.Default(construct.ByteSwapped(construct.Int), 6),
	'unk2' / construct.Default(construct.ByteSwapped(construct.Int), 0),
)