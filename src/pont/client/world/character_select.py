import construct

from pont.client.world.entities.player import Race, CombatClass, Gender
from pont.client.world.guid import Guid
from pont.utility.construct import Coordinates, PackEnum, FixedString, GuidConstruct

DisplayInfo = construct.Struct(
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
)

PetInfo = construct.Struct(
	'display_id' / construct.ByteSwapped(construct.Int),
	'level' / construct.ByteSwapped(construct.Int),
	'family' / construct.ByteSwapped(construct.Int),
)

ItemInfo = construct.Struct(
	'display_id' / construct.ByteSwapped(construct.Int),
	'inventory_type' / construct.Byte,
	'enchant_aura_id' / construct.ByteSwapped(construct.Int),
)

BagInfo = construct.Struct(
	'display_id' / construct.ByteSwapped(construct.Int),
	'inventory_type' / construct.Byte,
	'enchant_id' / construct.ByteSwapped(construct.Int),
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
	'zone' / construct.ByteSwapped(construct.Int),
	'map' / construct.ByteSwapped(construct.Int),
	'position' / construct.ByteSwapped(Coordinates()),
	'guild_guid' / construct.ByteSwapped(construct.Int),
	'flags' / construct.ByteSwapped(construct.Int),
	'customization_flags' / construct.ByteSwapped(construct.Int),
	# 'slot' / construct.Byte,
	'is_first_login' / construct.Flag,
	'pet' / PetInfo,
	'items' / construct.Array(19, ItemInfo),
	'bags' / construct.Array(4, BagInfo)
)
