import pont
from examples.chatbot.plugin import Plugin
from pont.log import logger
from pont.world import MessageType

class GuildLogPlugin(Plugin):
	def __init__(self):
		super().__init__()
		self._bot = None

	def load(self, bot):
		self._bot = bot
		@bot.on(pont.events.world.received_chat_message)
		async def _on_chat_message(message):
			if message.type == MessageType.guild:
				logger.info(f'{str(message)=}')

			return True