import collections
from typing import Optional

import pyee
import trio

import pont

from pont.client.auth import Realm
from pont.client.events import WorldEvent
from pont.client.world import WorldSession
from pont.client.world.expansions import Expansion
from pont.client.world.net.packets.auth_packets import AuthResponse
from pont.client.world.net.protocol import WorldServerProtocol
from pont.client.world.state import WorldState
from tests.client.cryptography import load_test_servers
from tests.mock.world import MockCharacter

logins_filename = 'C:\\Users\\Owner\\Documents\\WoW\\servers_config.json'
test_servers = load_test_servers(logins_filename)
ac_login = test_servers['acore']['account']
client_world: Optional[WorldSession] = None

class MemoryEmitter(pyee.TrioEventEmitter):
	Memory = collections.namedtuple('Memory', 'args, kwargs')

	def __init__(self, nursery=None, manager=None):
		super().__init__(nursery, manager)
		self.memory = {}

	def emit(self, event, *args, **kwargs):
		super().emit(event, *args, **kwargs)
		if event in self.memory.keys():
			self.memory[event].append(MemoryEmitter.Memory(args=args, kwargs=kwargs))
		else:
			self.memory[event] = [MemoryEmitter.Memory(args=args, kwargs=kwargs)]

async def client_login(stream, session_key, nursery):
	realm = Realm.parse(Realm.build({
		'name': 'horse',
		'address': ('127.0.0.1', 123),
		'num_characters': 1,
		'population': 0,
	}))

	emitter = MemoryEmitter(nursery)
	world = WorldSession(nursery=nursery, emitter=emitter)

	global client_world
	client_world = world
	assert world.state == WorldState.not_connected
	await world.connect(realm, stream=stream)
	assert emitter.memory == {WorldEvent.connected: [MemoryEmitter.Memory(args=(('127.0.0.1', 123),), kwargs={})]}

	assert world.state == WorldState.connected
	assert emitter.memory[WorldEvent.connected] == [((('127.0.0.1', 123),), {})]

	# Packet handler should not have been started
	assert not world._handling_packets
	await world.transfer(ac_login['username'], session_key)

	# Sanity check that this is the same as how we sent it
	assert world._crypto.server_seed == 7
	assert world._crypto.encryption_seed1 == 31
	assert world._crypto.encryption_seed2 == 71

	# Ensure packet handler is running
	assert 'pont.client.world.session.WorldSession._packet_handler' in str(world._parent_nursery.child_tasks)
	assert world._handling_packets
	assert WorldEvent.logging_in in emitter.memory
	assert 'new_listener' in emitter.memory
	assert WorldEvent.received_packet in emitter.memory
	assert WorldEvent.received_auth_response in emitter.memory
	assert WorldEvent.logged_in in emitter.memory
	nursery.cancel_scope.cancel()

async def world_server(stream, session_key, nursery):
	protocol = WorldServerProtocol(stream, session_key=session_key)
	await protocol.send_SMSG_AUTH_CHALLENGE(
		server_seed=7,
		encryption_seed1=31,
		encryption_seed2=71
	)

	# Sanity check that this is the same as how we sent it
	auth_session = await protocol.receive_CMSG_AUTH_SESSION()
	assert auth_session.header.size == 309
	assert auth_session.build == 12340
	assert auth_session.login_server_id == 0

	assert auth_session.login_server_type == 0
	assert auth_session.client_seed == client_world._crypto.client_seed

	assert auth_session.region_id == 0
	assert auth_session.dos_response == 3
	assert auth_session.account_name == 'DINNERTABLE'
	assert auth_session.realm_id == 1
	await protocol.send_SMSG_AUTH_RESPONSE(
		AuthResponse.ok, Expansion.wotlk
	)

async def test_session():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	session_key = 887638991071640811242800621506026194914017482863646559938463468713468253926173117812986327918380

	with trio.fail_after(4):
		async with trio.open_nursery() as nursery:
			nursery.start_soon(client_login, client_stream, session_key, nursery)
			nursery.start_soon(world_server, server_stream, session_key, nursery)

# async def test_session_logout():
# 	(client_stream, server_stream) = trio.testing.memory_stream_pair()
# 	session_key = 887638991071640811242800621506026194914017482863646559938463468713468253926173117812986327918380
#
# 	realm = Realm.parse(Realm.build({
# 		'name': 'horse',
# 		'address': ('127.0.0.1', 123),
# 		'num_characters': 1,
# 		'population': 0,
# 	}))
#
# 	async with trio.open_nursery() as nursery:
# 		emitter = MemoryEmitter(nursery)
# 		world = WorldSession(nursery=nursery, emitter=emitter)
#
# 		await world.connect(stream=client_stream, realm=realm)
# 		async with world.enter_world(MockCharacter(name='Pont')):
# 			await world.logout()