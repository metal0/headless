class Guid:
	def __init__(self, low: int = 0, high: int = 0):
		self.low: int = low
		self.high: int = high

	def __int__(self):
		return int(self.low | self.high)