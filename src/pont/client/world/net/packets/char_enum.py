import construct

from pont.utility.construct import PackEnum, GuidConstruct, Coordinates
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...guid import Guid
from ...character import CharacterNameResponse
from ...entities.player import Race, CombatClass, Gender

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
	'guid' / GuidConstruct(Guid),
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

CMSG_CHAR_ENUM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_ENUM, 0),
)

SMSG_CHAR_ENUM = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_ENUM, 4 + construct.len_(construct.this.characters)),
	'characters' / construct.PrefixedArray(construct.Byte, CharacterInfo),
)

CMSG_CHAR_RENAME = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_RENAME),
	'guid' / GuidConstruct(Guid),
	'new_name' / construct.CString('utf8')
)

RenameInfo = construct.Struct(
	'guid' / GuidConstruct(Guid),
	'new_name' / construct.CString('utf8')
)

SMSG_CHAR_RENAME = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_RENAME),
	'response' / PackEnum(CharacterNameResponse),
	'info' / construct.IfThenElse(
		(construct.this.response == CharacterNameResponse.no_name or
			construct.this.response == CharacterNameResponse.reserved), # also when == CHAR_CREATE_ERROR
		construct.Pass,
		RenameInfo,
	)
)