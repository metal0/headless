import construct

from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_BIND_POINT_UPDATE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_BIND_POINT_UPDATE, 8)
)