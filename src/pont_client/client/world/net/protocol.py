import trio

from pont_client.client import log
from pont_client.client.world.net import packets

log = log.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream

	async def receive_SMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		data = await self.stream.receive_some()
		return packets.SMSG_CHAR_ENUM.parse(data)


	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
