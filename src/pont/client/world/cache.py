import trio

from pont.client import events
from pont.client.world.net import Opcode
from pont.client.log import logger

class Cache:
	def __init__(self):
		self._storage = {}

	def __contains__(self, item):
		return item in self._storage

	def __len__(self):
		return len(self._storage)

	async def fetch(self, key):
		raise NotImplementedError()

	async def update(self, key):
		if key is None:
			return None

		response = await self.fetch(key)
		if response is None:
			return None

		self._storage[key] = response
		return response

	async def lookup(self, key):
		if key is None:
			return None

		if key in self._storage:
			return self._storage[key]

		return await self.update(key)

class NameCache(Cache):
	def __init__(self, world):
		super().__init__()
		self._world = world
		self._listener = world.emitter.on(events.world.received_name_query_response, self._handle_query_response)

	async def _handle_query_response(self, packet):
		if not packet.found:
			return

		self._storage[packet.guid] = packet.info

	async def fetch(self, guid):
		await self._world.protocol.send_CMSG_NAME_QUERY(guid=guid)

		with trio.fail_after(10):
			query_response = await self._world.wait_for_packet(opcode=Opcode.SMSG_NAME_QUERY_RESPONSE)

		if not query_response.found:
			return None

		return query_response.info
