import construct

from pont.utility.construct import Coordinates
from .headers import ServerHeader
from ..opcode import Opcode

SMSG_BIND_POINT_UPDATE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_BIND_POINT_UPDATE, 4*3 + 4 + 4),
	'position' / construct.ByteSwapped(Coordinates()),
	'map_id' / construct.Int32ul,
	'area_id' / construct.Int32ul,
)