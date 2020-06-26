import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.client.world.net.packets.headers import ClientHeader

CMSG_KEEP_ALIVE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_KEEP_ALIVE, 0)
)