import construct

from pont.client.world.net.packets.parse import parser
from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_CLIENTCACHE_VERSION = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CLIENTCACHE_VERSION, 4),
	'version' / construct.Default(construct.ByteSwapped(construct.Int), 3),
)

parser.set_parser(Opcode.SMSG_CLIENTCACHE_VERSION, SMSG_CLIENTCACHE_VERSION)