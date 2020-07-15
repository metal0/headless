class WorldError(Exception):
	pass

class ProtocolError(WorldError):
	pass

class Disconnected(ProtocolError):
	pass