from pont.utility.enum import ComparableEnum


class WorldState(ComparableEnum):
	disconnected = -1
	not_connected = 0
	connected = 1
	logging_in = 2
	in_queue = 3
	logged_in = 4

	loading = 5
	in_game = 6