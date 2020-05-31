from enum import Enum

class ComparableEnum(Enum):
	def __le__(self, other):
		return self.value < other.value

	def __ge__(self, other):
		return self.value > other.value