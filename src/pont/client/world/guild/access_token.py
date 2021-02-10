from enum import Enum

class Rights(Enum):
	none = 0
	guest = 1

	gm = 5

class Privileges(Enum):
	guild_invite = 1

class AccessToken:
	def __init__(self):
		pass

	def __str__(self):
		return ''

	def has_authority_to(self, rights: Rights):
		return False