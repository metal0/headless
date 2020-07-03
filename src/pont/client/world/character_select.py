import construct

from pont.client.world.entities.player import Race, CombatClass, Gender
from pont.client.world.guid import Guid
from pont.utility.construct import Coordinates, PackEnum, GuidConstruct

DisplayInfo = construct.Struct(
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
)

PetInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'level' / construct.Int32ul,
	'family' / construct.Int32ul,
)

ItemInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'inventory_type' / construct.Byte,
	'enchant_aura_id' / construct.Int32ul,
)

BagInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'inventory_type' / construct.Byte,
	'enchant_id' / construct.Int32ul,
)

CharacterInfo = construct.Struct(
	'guid' / construct.ByteSwapped(GuidConstruct(Guid)),
	'name' / construct.CString('ascii'),
	'race' / PackEnum(Race),
	'combat_class' / PackEnum(CombatClass),
	'gender' / PackEnum(Gender),
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
	'level' / construct.Byte,
	'zone' / construct.Int32ul,
	'map' / construct.Int32ul,
	'position' / construct.ByteSwapped(Coordinates()),
	'guild_guid' / construct.Int32ul,
	'flags' / construct.Int32ul,
	'customization_flags' / construct.Int32ul,
	# 'slot' / construct.Byte,
	'is_first_login' / construct.Flag,
	'pet' / PetInfo,
	'items' / construct.Array(19, ItemInfo),
	'bags' / construct.Array(4, BagInfo)
)
