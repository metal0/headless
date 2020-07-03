from ...utility import enum

class AuthState(enum.ComparableEnum):
	disconnected = -1
	not_connected = 0
	connected = 1
	logging_in = 2
	logged_in = 3
	realmlist_ready = 4
