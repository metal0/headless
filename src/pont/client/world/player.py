from typing import Optional

from pont.client.world.chat import chat
from pont.client.world.guild.guild import Guild


class LocalPlayer:
	def __init__(self, world):
		self._world = world
		self._guild: Optional[Guild] = None
		# languages known? default language?

	@property
	def guild(self):
		return self._guild

	async def say(self, message, language: chat.Language = chat.Language.common):
		await self._world.chat.send_message(message, chat.MessageType.say, language)

	async def yell(self, message, language: chat.Language = chat.Language.common):
		await self._world.chat.send_message(message, chat.MessageType.yell, language)

	async def send_guild_message(self, message, language: chat.Language = chat.Language.common):
		await self._world.chat.send_message(message, chat.MessageType.yell, language)

	async def whisper(self, message, recipient: str, language: chat.Language = chat.Language.common):
		await self._world.chat.send_message(message, chat.MessageType.whisper, language, recipient=recipient)

