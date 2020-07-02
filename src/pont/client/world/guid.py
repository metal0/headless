from enum import Enum
from typing import Optional

class GuidType(Enum):
	player = 0x0000

	item = 0x0040
	container = 0x0040

	dynamic_object = 0xF100
	corpse = 0xF101
	area_trigger = 0xF102
	game_object = 0xF110
	transport = 0xF120
	unit = 0xF130
	pet = 0xF140
	vehicle = 0xF150

	mo_transport = 0x1FC0
	instance = 0x1F40
	group = 0x1F50
	guild = 0x1FF0

class Guid:
	def __init__(self, counter: int = 0, high: int = 0, entry=None, value=None, type: Optional[GuidType] = None):
		self._set(counter, high, entry)

		if value is not None:
			self.value = value

		elif type is not None and value is None:
			self.type = type

	def __eq__(self, other):
		return self.value == other.value

	def _set(self, low: int, high: int, entry=None):
		if entry is not None:
			self.value = low | (entry << 24) | (high << 48)
		else:
			self.value = low | (high << 48)

	def has_entry(self):
		try:
			return self.type in (
				GuidType.item, GuidType.player, GuidType.dynamic_object,
				GuidType.corpse, GuidType.mo_transport, GuidType.instance,
				GuidType.group
			)
		except ValueError:
			return False

	@property
	def entry(self):
		if not self.has_entry():
			raise ValueError(f'Guid entry not supported by {self.type}')
		return (self.value >> 24) & 0x0000000000FFFFFF

	@property
	def counter(self):
		if self.has_entry():
			return self.value & 0x0000000000FFFFFF
		else:
			return self.value & 0x00000000FFFFFFFF

	@counter.setter
	def counter(self, value):
		self._set(value, self.high)

	@property
	def high(self):
		return (self.value >> 48) & 0x0000FFFF

	@high.setter
	def high(self, value):
		self._set(self.counter, value)

	@property
	def type(self) -> GuidType:
		try:
			return GuidType(self.high)
		except ValueError:
			return GuidType.player

	@type.setter
	def type(self, ty: GuidType):
		old_type = self.type
		self.high = ty.value | self.high & ~old_type.value

	@staticmethod
	def max_count() -> int:
		return 0xFFFFFFFF

	def __int__(self):
		return self.value

	def __str__(self):
		ty = self.type
		if ty is not None:
			return hex(self.value) + f', {ty}'
		else:
			return hex(self.value)