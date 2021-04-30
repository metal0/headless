import collections
import datetime

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

TimedEntry = collections.namedtuple('TimedEntry', ['timestamp', 'data'])

class TimedCache(Cache):
	def __init__(self, timeout: datetime.timedelta):
		super().__init__()
		self._timeout = timeout

	def __contains__(self, key):
		if key in self._storage:
			return not self.key_has_expired(key)
		return False

	def key_has_expired(self, key):
		return datetime.datetime.now() > (self._storage[key].timestamp + self._timeout)

	@property
	def timeout(self):
		return self._timeout

	async def update(self, key):
		if key is None:
			return None

		response = await self.fetch(key)
		if response is None:
			return None

		entry = TimedEntry(timestamp=datetime.datetime.now(), data=response)
		self._storage[key] = entry
		return entry.data

	async def lookup(self, key):
		if key is None:
			return None

		if key in self._storage:
			# Value expired
			if self.key_has_expired(key):
				return await self.update(key)
			else:
				return self._storage[key].data

		return await self.update(key)