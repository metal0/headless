import construct

from pont.world.net import Opcode
from pont.world.net.packets.headers import ServerHeader

SMSG_UPDATE_OBJECT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_UPDATE_OBJECT, 0),
	'data' / construct.GreedyBytes,
)

SMSG_COMPRESSED_UPDATE_OBJECT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, 0),
	'data' / construct.GreedyBytes
)
