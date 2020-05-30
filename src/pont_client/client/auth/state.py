from enum import Enum

class AuthState(Enum):
	not_connected = 0
	connected = 1
	logging_in = 2
	logged_in = 3
	realmlist_ready = 4

	def __le__(self, other):
		return self.value < other.value

	def __ge__(self, other):
		return self.value > other.value
