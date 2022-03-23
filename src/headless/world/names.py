import trio
from wlink.guid import GuidType
from wlink.world.packets import Opcode, make_CMSG_NAME_QUERY, CMSG_NAME_QUERY

from headless.utility.cache import Cache

class NameCache(Cache):
	def __init__(self, world, fail_after=60):
		super().__init__()
		self._world = world
		self._fail_after = fail_after

	async def fetch(self, guid):
		if guid.type == GuidType.player:
			if guid.value == 0:
				return None

			await self._world.stream.send_encrypted_packet(CMSG_NAME_QUERY, make_CMSG_NAME_QUERY(guid=guid))
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
