import construct

from pont_client.client.world.net.packets import parser
from pont_client.client.world.net.packets.constants import Opcode
from pont_client.client.world.net.packets.headers import ServerHeader

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'header' / ServerHeader(20),
	'map' / construct.Int,
	'x' / construct.Float32b,
	'y' / construct.Float32b,
	'z' / construct.Float32b,
	'rotation' / construct.Float32b,
)

parser.set_parser(Opcode.SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGIN_VERIFY_WORLD)