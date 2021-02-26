from enum import Enum

class CharacterNameResponse(Enum):
	success = 0x57
	failure = 0x58
	no_name = 0x59
	too_share = 0x5A
	too_long = 0x5B
	invalid_character = 0x5C
	mixed_languages = 0x5D
	profane = 0x5E
	reserved = 0x5F
	invalid_apostrophes = 0x60
	multiple_apostrophes = 0x61
	three_consecutive = 0x62
	invalid_space = 0x63
	consecutive_spaces = 0x64
	russian_consecutive_silent_characters = 0x65
	russian_silent_character_at_beginning_or_end = 0x66
	declension_doesnt_match_base_name = 0x67