class Position:
	def __init__(self, x: float = 0, y: float = 0, z: float = 0):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return f'({self.x}, {self.y}, {self.z})'

	def __eq__(self, other):
		try:
			return self.x == other[0] and self.y == other[1] and self.z == other[2]
		except AttributeError:
			return self.x == other.x and self.y == other.y and self.z == other.z
