import construct

from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_TUTORIAL_FLAGS = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TUTORIAL_FLAGS, 4 * 8),
	'tutorials' / construct.ByteSwapped(construct.Array(8, construct.Int))
)
