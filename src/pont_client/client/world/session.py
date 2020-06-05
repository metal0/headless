import trio
from trio_socks import socks5
from typing import Optional, Tuple

from pont_client.client.world.net.protocol import WorldProtocol
from .. import log, auth

log = log.get_logger(__name__)

class WorldSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]] = None):
		self.proxy = proxy
		self.protocol: Optional[WorldProtocol] = None
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self.__session_key = None
		# self._world = esper.World
		# self.__encrypt = lambda data: rc4.rc4(data, bytes.fromhex('C2B3723CC6AED9B5343C53EE2F4367CE'))
		# self.__decrypt = lambda data: rc4.rc4(data, bytes.fromhex('CC98AE04E897EACA12DDC09342915357'))

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()

	async def enter_world(self, realm: auth.Realm, proxy=None, stream=None):
		realm_address = realm.address.split(':')
		if stream is None:
			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(destination=realm_address,
				                                   proxy=proxy or self.proxy or None)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*realm_address)
		else:
			self._stream = stream

		self.protocol = WorldProtocol(stream=self._stream)
		await self.protocol.spawn_receiver(self._stream, nursery=self._nursery, emitter=self._emitter)

# class WorldSession(ScopedEmitter):
# 	def __init__(self, context):
# 		super().__init__(context.emitter)
# 		self.context = context
# 		self.world_handler = WorldHandler(context=context)
# 		self.protocol = None
# 		self.__state = WorldState.not_connected
# 		self.__session_key = None
# 		self.__encrypt = lambda data: rc4.rc4(data, bytes.fromhex('C2B3723CC6AED9B5343C53EE2F4367CE'))
# 		self.__decrypt = lambda data: rc4.rc4(data, bytes.fromhex('CC98AE04E897EACA12DDC09342915357'))
# 		self.__host = None
# 		self.__port = None
# 		self._stream = None