import trio
from wlink.guid import GuidType
from wlink.world import Opcode

from pont.utility.cache import Cache

class NameCache(Cache):
	def __init__(self, world, fail_after=10):
		super().__init__()
		self._world = world
		self._fail_after = fail_after

	async def fetch(self, guid):
		if guid.type == GuidType.player:
			await self._world.protocol.send_CMSG_NAME_QUERY(guid=guid)
		elif guid.type == GuidType.guild:
			pass

		try:
			with trio.fail_after(self._fail_after):
				query_response = await self._world.wait_for_packet(opcode=Opcode.SMSG_NAME_QUERY_RESPONSE)
		except trio.TooSlowError:
			return None

		if not query_response.found:
			return None

		return query_response.info
