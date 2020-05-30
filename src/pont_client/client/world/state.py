from enum import Enum
from uuid import uuid4

class WorldState(Enum):
	disconnected = -1
	not_connected = 0
	connected = 1
	in_game = 2