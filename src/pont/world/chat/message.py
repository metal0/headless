import datetime

from enum import Enum

class MessageType(Enum):
	system = 0x00
	say = 0x01
	party = 0x02
	raid = 0x03
	guild = 0x04
	officer = 0x05
	yell = 0x06
	whisper = 0x07
	whisper_foreign = 0x08
	whisper_inform = 0x09
	emote = 0x0a
	text_emote = 0x0b
	monster_say = 0x0c
	monster_party = 0x0d
	monster_yell = 0x0e
	monster_whisper = 0x0f
	monster_emote = 0x10
	channel = 0x11
	channel_join = 0x12
	channel_leave = 0x13
	channel_list = 0x14
	channel_notice = 0x15
	channel_notice_user = 0x16
	afk = 0x17
	dnd = 0x18
	ignored = 0x19
	skill = 0x1a
	loot = 0x1b
	money = 0x1c
	opening = 0x1d
	tradeskills = 0x1e
	pet_info = 0x1f
	combat_misc_info = 0x20
	combat_xp_gain = 0x21
	combat_honor_gain = 0x22
	combat_faction_change = 0x23
	bg_system_neutral = 0x24
	bg_system_alliance = 0x25
	bg_system_horde = 0x26
	raid_leader = 0x27
	raid_warning = 0x28
	raid_boss_emote = 0x29
	raid_boss_whisper = 0x2a
	filtered = 0x2b
	battleground = 0x2c
	battleground_leader = 0x2d
	restricted = 0x2e
	battlenet = 0x2f
	achievement = 0x30
	guild_achievement = 0x31
	arena_points = 0x32
	party_leader = 0x33
	addon = 0xFFFFFFFF

class ChatLinkColor(Enum):
	trade       = 0xffffd000  # orange
	talent      = 0xff4e96f7  # blue
	spell       = 0xff71d5ff  # bright blue
	enchant     = 0xffffd000  # orange
	achievement = 0xffffff00  # achievement yellow
	glyph       = 0xff66bbff  # teal blue

class ChatMessage:
	@staticmethod
	def is_whisper(packet):
		return packet.message_type in (
	MessageType.whisper, MessageType.whisper_foreign, MessageType.whisper_inform,
	MessageType.monster_whisper, MessageType.raid_boss_whisper
)

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

	def __init__(self, world, packet, sender, receiver):
		self._world = world
		self._packet = packet
		self._sender = sender
		self._receiver = receiver

		self.time = datetime.time()

	@property
	def text(self):
		return self._packet.text

	@property
	def type(self):
		return self._packet.message_type

	@property
	def sender(self):
		return self._sender

	@property
	def receiver(self):
		return self._receiver

	@property
	def language(self):
		return self._packet.language

	def __str__(self):
		if self.sender is None:
			return f'[{self.type}]: {self.text}'

		if self.receiver is None:
			return f'[{self.sender}] [{self.type}]: {self.text}'

		return f'[{self.sender} -> {self.receiver}] [{self.type}]: {self.text}'