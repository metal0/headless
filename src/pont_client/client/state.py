from enum import Enum

class ClientState(Enum):
	not_connected = 1
	logging_in = 2
	realmlist = 3
	character_select = 4
	loading_world = 5
	in_game = 6
