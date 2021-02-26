from pont.client.world.chat import Chat

class LocalPlayer:
	def __init__(self, world, guid, name, guild=None):
		self._world = world
		self._guild = guild
		self._chat = Chat(world)
		self._guid = guid
		self._name = name
		# languages known? default language?

	@property
	def guid(self):
		return self._guid

	@property
	def chat(self):
		return self._chat

	@property
	def guild(self):
		return self._guild

