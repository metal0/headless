from typing import Optional

from pont.client.world.guild.guild import Guild
from pont.client.world.language import Language
from pont.client.world.chat import MessageType, Chat


class LocalPlayer:
	def __init__(self, world):
		self._world = world
		self._guild: Optional[Guild] = None
		self._chat = Chat(world)
		# languages known? default language?

	@property
	def chat(self):
		return self._chat

	@property
	def guild(self):
		return self._guild

