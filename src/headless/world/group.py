from wlink.world.packets import GroupType


class Group:
	def __init__(self, world, packet=None):
		self.world = world
		self._packet = packet

	def update(self, packet=None):
		self._packet = packet

	@property
	def is_empty(self) -> bool:
		return self._packet is not None

	@property
	def leader(self):
		return self._packet.leader_guid

	@property
	def type(self):
		if self._packet is None:
			return GroupType.party

		return self._packet.type

	@property
	def members(self):
		if self._packet is None:
			return []
		return list(self._packet.members)

	@property
	def size(self):
		if self._packet is None:
			return 0

		return self._packet.size

	def __len__(self):
		return self.size