from pont.client.world import Guid
from pont.client.world.cache import Cache

count = 0
class TestCache(Cache):
	async def fetch(self, key):
		global count
		result = f'{key}: {count}'
		count += 1
		return result

async def test_cache():
	cache = TestCache()
	assert await cache.update(0) == '0: 0'
	assert cache._storage == {0: '0: 0'}

	assert await cache.lookup(0) == '0: 0'
	assert cache._storage == {0: '0: 0'}

	assert await cache.update(0) == '0: 1'
	assert cache._storage == {0: '0: 1'}

	await cache.update(1)
	assert cache._storage == {0: '0: 1', 1: '1: 2'}

	await cache.lookup(2)
	assert cache._storage == {0: '0: 1', 1: '1: 2', 2: '2: 3'}

	cache = TestCache()
	assert len(cache) == 0
	assert await cache.lookup(Guid(10)) == f'{Guid(10)}: 4'
	assert cache._storage == {Guid(10): f'{Guid(10)}: 4'}
	assert Guid(10) in cache
	assert Guid(11) not in cache