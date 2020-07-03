import construct

from .constants import Opcode
from .headers import ServerHeader
from .parse import parser

SMSG_INIT_WORLD_STATES = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_INIT_WORLD_STATES, 14),
	'map_id' / construct.Int32ul,
	'zone_id' / construct.Int32ul,
	'area_id' / construct.Int32ul,
	'world_states' / construct.PrefixedArray(construct.Int16ul, construct.Sequence(construct.Int32ul, construct.Int32ul)),
)

parser.set_parser(Opcode.SMSG_INIT_WORLD_STATES, SMSG_INIT_WORLD_STATES)