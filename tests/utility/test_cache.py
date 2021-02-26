import trio
import datetime
from pont.client.world import Guid
from pont.client.world.names import NameCache
from pont.client.world.net import WorldClientProtocol
from pont.utility.cache import Cache, TimedCache
from tests.mock.world import MockQueryResponse, MockNameInfo, MockWorld

count = 0
class MockCache(Cache):
	async def fetch(self, key):
		global count
		result = f'{key}: {count}'
		count += 1
		return result

timed_count = 0
class MockTimedCache(TimedCache):
	async def fetch(self, key):
		global timed_count
		result = f'{key}: {timed_count}'
		timed_count += 1
		return result

def unit_normalize(cache):
	return cache._storage

def timed_normalize(cache):
	return {k: v.data for k, v in unit_normalize(cache).items()}

async def default_cache_test(cache_type, normalize_storage):
	cache = cache_type()
	assert await cache.update(0) == '0: 0'
	assert normalize_storage(cache) == {0: '0: 0'}

	assert await cache.lookup(0) == '0: 0'
	assert normalize_storage(cache) == {0: '0: 0'}

	assert await cache.update(0) == '0: 1'
	assert normalize_storage(cache) == {0: '0: 1'}

	await cache.update(1)
	assert normalize_storage(cache) == {0: '0: 1', 1: '1: 2'}

	await cache.lookup(2)
	assert normalize_storage(cache) == {0: '0: 1', 1: '1: 2', 2: '2: 3'}

	cache = cache_type()
	assert len(cache) == 0
	assert await cache.lookup(Guid(10)) == f'{Guid(10)}: 4'
	print(normalize_storage(cache))
	assert normalize_storage(cache) == {Guid(10): f'{Guid(10)}: 4'}
	assert Guid(10) in cache
	assert Guid(11) not in cache

async def test_cache():
	cache_type = MockCache
	await default_cache_test(cache_type, unit_normalize)

async def test_timed_cache():
	cache_type = lambda: MockTimedCache(timeout=datetime.timedelta(seconds=1))
	await default_cache_test(cache_type, timed_normalize)

	# Test time expiration property
	cache = MockTimedCache(timeout=datetime.timedelta(milliseconds=100))
	await cache.update(0)
	assert 0 in cache
	await trio.sleep(0.1)
	assert 0 not in cache

async def mock_wait_for_packet(opcode):
	return MockQueryResponse(found=True, info=MockNameInfo(name='Pont'))

async def test_name_cache():
	(client, server) = trio.testing.memory_stream_pair()
	protocol = WorldClientProtocol(client, session_key=7)
	world = MockWorld(protocol=protocol, wait_for_packet=mock_wait_for_packet)
	cache = NameCache(world)
	assert (await cache.lookup(Guid(0x1))).name == 'Pont'
	assert Guid(0x1) in cache
