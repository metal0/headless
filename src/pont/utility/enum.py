from enum import Enum

class ComparableEnum(Enum):
	def __lt__(self, other):
		return self.value < other.value

	def __gt__(self, other):
		return self.value > other.value

	def __le__(self, other):
		return self < other or self.value == other.value

	def __ge__(self, other):
		return self > other or self.value == other.value