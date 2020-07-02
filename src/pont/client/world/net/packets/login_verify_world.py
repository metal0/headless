import construct

from pont.client.world.net.packets.parse import parser
from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader
from pont.utility.construct import Coordinates

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGIN_VERIFY_WORLD, 20),
	'map' / construct.ByteSwapped(construct.Int),
	'position' / construct.ByteSwapped(Coordinates()),
	'rotation' / construct.ByteSwapped(construct.Float32b),
)

parser.set_parser(Opcode.SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGIN_VERIFY_WORLD)