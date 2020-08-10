from ..errors import ProtocolError
from .message import MessageType
from ..language import Language
from ..state import WorldState

class Chat:
	def __init__(self, world):
		self._world = world
		if world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		# world.
	# async def _handle_message(self, message):
	# 	while True:

	async def send_message(self, text: str, message_type: MessageType, language: Language):
		if self._world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

		await self._world.protocol.send_CMSG_MESSAGECHAT(text, message_type, language)
