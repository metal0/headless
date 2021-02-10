from typing import Optional

from .message import MessageType
from ..errors import ProtocolError
from ..language import Language
from ..state import WorldState
from ... import events
from ...log import logger

class Chat:
	def __init__(self, world):
		self._world = world
		self._messages = []
		if world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		self._world.emitter.on(events.world.received_chat_message, self._message_handler)

	@property
	def messages(self):
		return self._messages

	def _message_handler(self, message):
		logger.log('MESSAGES', f'{str(message)=}')
		self._messages.append(message)

	async def send_message(self, text: str, message_type: MessageType, language: Language, recipient: Optional[str]=None):
		if self._world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		await self._world.protocol.send_CMSG_MESSAGECHAT(text, message_type, language, recipient=recipient)
		self._world.emitter.emit(events.world.sent_chat_message, text=text, type=message_type, language=language, recipient=recipient)

	async def say(self, message, language: Language = Language.common):
		await self.send_message(message, MessageType.say, language)

	async def yell(self, message, language: Language = Language.common):
		await self.send_message(message, MessageType.yell, language)

	async def guild(self, message, language: Language = Language.common):
		await self.send_message(message, MessageType.guild, language)

	async def whisper(self, message, recipient: str, language: Language = Language.common):
		await self.send_message(message, MessageType.whisper, language, recipient=recipient)