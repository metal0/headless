import construct

from .constants import Opcode
from pont_client.utility.construct import PackEnum, Coordinates

CharacterInfo = construct.Struct(
	'name' / construct.CString('ascii'),
	'race' / construct.Byte,
	'class' / construct.Byte,
	'gender' / construct.Byte,
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
	'level' / construct.Byte,
	'zone' / construct.Bytes(4),
	'map' / construct.Bytes(4),
	'coords' / Coordinates(),
)

SMSG_CHAR_ENUM = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.SMSG_CHAR_ENUM, PackEnum(Opcode)), Opcode.SMSG_CHAR_ENUM),
	'guid' / construct.Int,
	'characters' / CharacterInfo
)


