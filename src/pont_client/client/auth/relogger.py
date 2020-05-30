import trio

from pont import events, log
log = log.get_logger(__name__)

class Relogger:
	on_relog = None
	def __init__(self, context, emitter):
		self.__context = context
		self.__emitter = emitter
		self.__relogging = False

	def start(self):
		if not self.__context.config.relogger:
			return

		async def on_relog(*args, **kwargs):
			log.debug(f'on_relog called!')
			if self.__relogging:
				return

			await trio.sleep(10)
			await self.__context.authenticate(self.__context.config.username, self.__context.config.password)

		self.__emitter.on(events.auth.disconnected, on_relog)
		self.__emitter.on(events.auth.invalid_login, on_relog)

