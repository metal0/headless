import construct

from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_CLIENTCACHE_VERSION = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CLIENTCACHE_VERSION, 4),
	'version' / construct.Default(construct.Int32ul, 3),
)
