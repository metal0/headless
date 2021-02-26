import construct

from pont.client.world.net.opcode import Opcode
from pont.client.world.net.packets.headers import ServerHeader

# TODO: There is DOS potential here as well as with SMSG_ADDON_INFO as mentioned on the TrinityCore Github.
#  I suspect this is due to world protocol using zlib DEFLATE compression, which is susceptible to decompression bombs.
#  Though I don't know how effective this will be in the context of TCP streams.
SMSG_ADDON_INFO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_ADDON_INFO, 4),
	'data' / construct.Bytes(construct.this.header.size - 2),
)

SMSG_CLIENTCACHE_VERSION = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CLIENTCACHE_VERSION, 4),
	'version' / construct.Default(construct.Int32ul, 3),
)

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

SMSG_UPDATE_WORLD_STATES = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_UPDATE_WORLD_STATE, 4 + 4),
	'field' / construct.Int32ul,
	'value' / construct.Int32ul
)