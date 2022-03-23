import datetime
from typing import Optional
from wlink.log import logger
from wlink.world.errors import ProtocolError
from wlink.world.packets import Language, MessageType, CMSG_MESSAGECHAT
from wlink.world.packets.b12340.chat_packets import make_CMSG_MESSAGECHAT

from ..state import WorldState
from ... import events

class LocalChat:
	def __init__(self, world):
		self._world = world
		self._messages = []
		if world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		@world.emitter.on(events.world.received_duel_winner)
		async def _on_duel_winner(packet):
			if packet.loser_fled:
				self.add_message(f'{packet.loser} has fled from {packet.winner} in a duel')
			else:
				self.add_message(f'{packet.winner} has defeated {packet.loser} in a duel')

		@world.emitter.on(events.world.received_guild_invite)
		async def _on_guild_invite(packet):
			self.add_message(f'{packet.inviter} has invited you to join {packet.guild}')

		@world.emitter.on(events.world.received_group_invite)
		async def _on_group_invite(packet):
			if packet.can_accept:
				self.add_message(f'{packet.inviter} has invited you to join a group')
			else:
				self.add_message(f'{packet.inviter} invited you to a group, but you could not accept because you are already in a group.')

		self._world.emitter.on(events.world.received_chat_message, self.add_message)
		self._world.emitter.on(events.world.received_motd, lambda packet: self.add_message(packet))

	@property
	def messages(self):
		return [message[0] for message in self._messages]

	def messages_since(self, timepoint: datetime.datetime):
		return [ message[0] for message in self.messages if timepoint > message[1]]

	@staticmethod
	def format_chat_event(message):
		if getattr(message, 'lines', None):
			text = ' '.join(message.lines)
			return f'[System] [motd]: {text}'

		elif getattr(message, 'text', None):
			return str(message)

		return str(message)

	def add_message(self, message):
		if getattr(message, 'language', None) is not None:
			if message.language in (Language.addon, ):
				return

		message = LocalChat.format_chat_event(message)
		self.display(message)

	async def message(self, text: str, message_type: MessageType, language: Language, recipient: Optional[str] = None):
		if self._world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		await self._world.stream.send_encrypted_packet(CMSG_MESSAGECHAT, make_CMSG_MESSAGECHAT(
			text, message_type, language, recipient=recipient
		))

		self._world.emitter.emit(events.world.sent_chat_message, text=text, type=message_type, language=language, recipient=recipient)

	async def say(self, message, language: Language = Language.common):
		await self.message(message, MessageType.say, language)

	async def raid(self, message, language: Language = Language.common):
		# TODO: Figure out if we're leader or not
		await self.message(message, MessageType.raid, language)

	async def party(self, message, language: Language = Language.common):
		# TODO: Figure out if we're leader or not
		await self.message(message, MessageType.party, language)

	async def yell(self, message, language: Language = Language.common):
		await self.message(message, MessageType.yell, language)

	async def guild(self, message, language: Language = Language.common):
		await self.message(message, MessageType.guild, language)

	async def whisper(self, message, recipient: str, language: Language = Language.common):
		await self.message(message, MessageType.whisper, language, recipient=recipient)

	def display(self, text: str):
		self._messages.append((text, datetime.datetime.now()))
		logger.log('MESSAGES', text)
