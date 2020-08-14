import construct

from pont.client.world.net.opcode import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_INITIALIZE_FACTIONS = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_INITIALIZE_FACTIONS, 4 + 128*5),
	'unknown' / construct.Default(construct.Int32ul, 0x00000080),
)

# TODO: SMSG_SET_FACTION_STANDING
SMSG_SET_FACTION_STANDING = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_SET_FACTION_STANDING, 17),
	construct.Padding(4),
	'send_faction_increased' / construct.Byte,
)