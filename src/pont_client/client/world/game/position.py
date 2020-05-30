from pont import log
log = log.get_logger(__name__)

class Position:
	def __init__(self, x: float = 0, y: float = 0, z: float = 0, rot: float = 0):
		self.x = x
		self.y = y
		self.z = z
		self.rot = rot