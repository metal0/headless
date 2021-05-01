from typing import Optional

from wlink.log import logger
from wlink.world.errors import ProtocolError
from wlink.world.packets import Language

from .message import MessageType, ChatMessage
from ..state import WorldState
from ... import events


class Chat:
	def __init__(self, world):
		self._world = world
		self._messages = []
		if world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		self._world.emitter.on(events.world.received_chat_message, self.handle_message)
		self._world.emitter.on(events.world.received_motd, lambda packet: self.handle_message(packet))

	@property
	def messages(self):
		return self._messages

	@staticmethod
	def format_chat_event(message):
		if getattr(message, 'lines', None):
			text = ' '.join(message.lines)
			return f'[System] [motd]: {text}'

		elif getattr(message, 'text', None):
			return str(message)

		return str(message)

	def handle_message(self, message):
		if getattr(message, 'language', None) is not None:
			if message.language in (Language.addon, ):
				return

		message = Chat.format_chat_event(message)
		self._messages.append(message)
		self.display(message)

	async def message(self, text: str, message_type: MessageType, language: Language, recipient: Optional[str] = None):
		if self._world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		await self._world.protocol.send_CMSG_MESSAGECHAT(text, message_type, language, recipient=recipient)
		self._world.emitter.emit(events.world.sent_chat_message, text=text, type=message_type, language=language, recipient=recipient)

	async def say(self, message, language: Language = Language.common):
		await self.message(message, MessageType.say, language)

	async def yell(self, message, language: Language = Language.common):
		await self.message(message, MessageType.yell, language)

	async def guild(self, message, language: Language = Language.common):
		await self.message(message, MessageType.guild, language)

	async def whisper(self, message, recipient: str, language: Language = Language.common):
		await self.message(message, MessageType.whisper, language, recipient=recipient)

	def display(self, text: str):
		logger.log('MESSAGES', text)
