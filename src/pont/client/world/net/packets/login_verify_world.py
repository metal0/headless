import construct

from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader
from pont.utility.construct import Coordinates

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGIN_VERIFY_WORLD, 20),
	'map' / construct.Int32ul,
	'position' / construct.ByteSwapped(Coordinates()),
	'rotation' / construct.Float32l,
)
