from headless import events
from headless.world.chat import LocalChat
from headless.world.group import Group
from headless.log import logger

class LocalPlayer:
	def __init__(self, world, guid, name, guild=None):
		self.world = world
		self._guild = guild
		self._chat = world.chat
		self._guid = guid
		self._name = name
		self._group = None

		@world.emitter.on(events.world.received_group_invite)
		def _on_group_invite(packet):
			if self._group is None:
				self._group = Group(world)

		@world.emitter.on(events.world.received_group_list)
		def _on_group_list(packet):
			self._group = Group(world, packet)
			if self._group.size > 0:
				logger.info(f'Joined group')

		@world.emitter.on(events.world.received_group_destroyed)
		def _on_group_destroy(packet):
			self._group = None
			logger.info(f'Left group')

		@world.emitter.on(events.world.received_group_kick)
		def _on_group_kick(packet):
			self._group = None
			logger.info(f'Kicked from group')

	# languages known? default language?

	@property
	def group(self):
		return self._group

	@property
	def guid(self):
		return self._guid

	@property
	def chat(self):
		return self._chat

	@property
	def guild(self):
		return self._guild

	@property
	def name(self):
		return self._name

	async def accept_duel(self):
		await self.world.protocol.send_CMSG_DUEL_ACCEPTED()

	async def leave_group(self):
		await self.world.protocol.send_CMSG_GROUP_DISBAND()

	async def send_group_invite(self, name: str):
		await self.world.protocol.send_CMSG_GROUP_INVITE(name)