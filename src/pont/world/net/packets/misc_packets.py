import construct

from pont.world.net.opcode import Opcode
from pont.world.net.packets.headers import ServerHeader

SMSG_TRIGGER_CINEMATIC = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TRIGGER_CINEMATIC, 4),
	'cinematic_id' / construct.Int32ul
)
SMSG_TRIGGER_MOVIE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TRIGGER_MOVIE, 4),
	'movid_id' / construct.Int32ul
)

SMSG_INIT_WORLD_STATES = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_INIT_WORLD_STATES, 14),
	'map_id' / construct.Int32ul,
	'zone_id' / construct.Int32ul,
	'area_id' / construct.Int32ul,
	'world_states' / construct.PrefixedArray(construct.Int16ul, construct.Sequence(construct.Int32ul, construct.Int32ul)),
)