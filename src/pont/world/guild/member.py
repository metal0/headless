from enum import Enum

class MemberStatus(Enum):
	offline = 0
	online = 1
	afk = 2
	dnd = 4
	mobile = 8

class GuildMember:
	pass