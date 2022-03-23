import datetime
import textwrap
from enum import Enum
from typing import Optional

from wlink.log import logger
from wlink.world.packets import MessageType

class ChatLinkColor(Enum):
	trade       = 0xffffd000  # orange
	talent      = 0xff4e96f7  # blue
	spell       = 0xff71d5ff  # bright blue
	enchant     = 0xffffd000  # orange
	achievement = 0xffffff00  # achievement yellow
	glyph       = 0xff66bbff  # teal blue

class ChatMessage:
	max_length = 255

	@staticmethod
	def is_whisper(type):
		return type in (
	MessageType.whisper, MessageType.whisper_foreign, MessageType.whisper_inform,
	MessageType.monster_whisper, MessageType.raid_boss_whisper
)
	@staticmethod
	def is_nearby_chat(type):
		return type in (
			MessageType.say, MessageType.emote, MessageType.text_emote, MessageType.monster_emote,
			MessageType.monster_say,
		)

	@staticmethod
	def is_guild_chat(type):
		return type in (MessageType.guild, MessageType.guild_achievement, MessageType.officer)

	@staticmethod
	def is_raid_message(type):
		return type in (MessageType.raid_leader, MessageType.raid, MessageType.raid_warning,
			MessageType.battleground_leader, MessageType.battleground, MessageType.bg_system_alliance,
		)

	@staticmethod
	def is_party_message(type):
		return type in (MessageType.party, MessageType.party_leader, MessageType.monster_party)

	@staticmethod
	def is_group_message(type):
		return ChatMessage.is_raid_message(type) or type in (MessageType.party, MessageType.party_leader)

	@staticmethod
	def is_monster_message(packet):
		return packet.message_type in (
			MessageType.monster_say, MessageType.monster_emote,
			MessageType.monster_party, MessageType.monster_yell,
			MessageType.monster_whisper, MessageType.raid_boss_emote,
			MessageType.raid_boss_whisper
		)

	@staticmethod
	async def load_message(world, packet):
		receiver = None
		if ChatMessage.is_monster_message(packet) or packet.message_type == MessageType.whisper_foreign:
			sender = packet.info.sender
		else:
			sender = (await world.names.lookup(packet.sender_guid))
			if sender is not None:
				sender = sender.name

		if ChatMessage.is_whisper(packet):
			receiver = (await world.names.lookup(world.local_player.guid)).name
			if receiver is not None:
				receiver = receiver.name

		return ChatMessage(world, packet, sender, receiver)

	def __init__(self, world, packet, sender: Optional[str], receiver: Optional[str]):
		self._world = world
		self._packet = packet
		self._sender = sender
		self._receiver = receiver

		self.time = datetime.datetime.now()

	@property
	def text(self):
		return self._packet.text

	@property
	def type(self):
		return self._packet.message_type

	@property
	def sender(self) -> Optional[str]:
		return self._sender

	@property
	def receiver(self) -> Optional[str]:
		return self._receiver

	@property
	def language(self):
		return self._packet.language

	def __str__(self):
		return ChatMessage.format(self.text, self.type, self.sender, self.receiver)

	@staticmethod
	def format(text: str, message_type: MessageType, sender: Optional[str], receiver: Optional[str]):
		if message_type == MessageType.system:
			return f'[System]: {text}'

		type_string = str(message_type).replace("MessageType.", "").replace('system', 'System')
		if sender is None:
			return f'[{type_string}]: {text}'

		if receiver is None:
			return f'[{sender}] [{type_string}]: {text}'

		return f'[{sender} -> {receiver}] [{type_string}]: {text}'

	async def reply(self, text: str):
		if len(text) > ChatMessage.max_length:
			for chunk in textwrap.wrap(text, ChatMessage.max_length, replace_whitespace=False):
				await self.reply(chunk)
			return

		if self._world.chat is None:
			return

		try:
			if ChatMessage.is_whisper(self.type):
				await self._world.chat.whisper(text, self.sender, self.language)

			elif ChatMessage.is_guild_chat(self.type):
				await self._world.chat.guild(text, self.language)

			elif ChatMessage.is_nearby_chat(self.type):
				await self._world.chat.say(text, self.language)

			elif ChatMessage.is_raid_message(self.type):
				await self._world.chat.raid(text, self.language)

			elif ChatMessage.is_party_message(type):
				await self._world.chat.party(text, self.language)

		except Exception as e:
			logger.exception(e)

	async def flush(self):
		pass