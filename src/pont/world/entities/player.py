from enum import Enum

class Race(Enum):
	none = 0
	human = 1
	orc = 2
	dwarf = 3
	night_elf = 4
	undead = 5
	tauren = 6
	gnome = 7
	troll = 8
	blood_elf = 10
	draenai = 11

def is_alliance(race: Race) -> bool:
	return race in (Race.human, Race.dwarf, Race.gnome, Race.draenai, Race.night_elf)

def is_horde(race: Race) -> bool:
	return race in (Race.orc, Race.undead, Race.tauren, Race.troll, Race.blood_elf)

class CombatClass(Enum):
	none = 0
	warrior = 1
	paladin = 2
	hunter = 3
	rogue = 4
	priest = 5
	death_knight = 6
	shaman = 7
	mage = 8
	warlock = 9
	druid = 11

class Gender(Enum):
	male = 0
	female = 1
	none = 2
