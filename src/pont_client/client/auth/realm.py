import construct
from enum import Enum
from ...utility.construct import PackEnum, AddressPort


class RealmType(Enum):
	normal = 0
	pvp = 1
	normal2 = 4
	rp = 6
	rp_pvp = 8
	max_realm_type = 14

class RealmPopulation(Enum):
	high = 3
	medium = 2
	low = 0

class RealmStatus(Enum):
	online = 0
	unavailable = 1
	offline = 2

class RealmFlags(Enum):
	none = 0
	unavailable = 1
	offline = 2
	specify_build = 4
	unknown1 = 8
	unknown2 = 0x10
	new_players = 0x20
	recommended = 0x40
	full = 0x80

	def __and__(self, other):
		value = self.value & other.value
		return RealmFlags(value)

BuildInfo = construct.Struct(
	'major' / construct.Default(construct.Byte, 3),
	'minor' / construct.Default(construct.Byte, 3),
	'bugfix' / construct.Default(construct.Byte, 5),
	'build' / construct.Default(construct.ByteSwapped(construct.Short), 12340),
)

Realm = construct.Struct(
	'type' / construct.Default(PackEnum(RealmType), RealmType.pvp),
	'status' / construct.Default(PackEnum(RealmStatus), RealmStatus.online),
	'flags' / construct.Default(PackEnum(RealmFlags), RealmFlags.none),
	'name' / construct.CString('ascii'),
	'address' / AddressPort('ascii'),
	'population' / construct.ByteSwapped(construct.Float32b),
	'num_characters' / construct.Byte,
	'timezone' / construct.Default(construct.Byte, 8),
	'id' / construct.Default(construct.Byte, 1),
	'build_info' / construct.Switch(
		(construct.this.flags & RealmFlags.specify_build) == RealmFlags.specify_build.value,
		{
			True: BuildInfo,
			False: construct.Pass
		}
	)
)