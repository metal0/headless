import collections
import json
import os

import construct
import pyee
import pytest
import trio
from typing import Optional

from wlink import Guid
from wlink.auth.realm import Realm
from wlink.world import WorldServerStream
from wlink.world.errors import ProtocolError
from wlink.world.packets import AuthResponse, Expansion, make_SMSG_AUTH_RESPONSE, make_CMSG_PLAYER_LOGIN, \
	CMSG_PLAYER_LOGIN, make_SMSG_LOGIN_VERIFY_WORLD, CMSG_AUTH_SESSION, make_SMSG_AUTH_CHALLENGE, SMSG_AUTH_CHALLENGE, \
	SMSG_AUTH_RESPONSE, SMSG_LOGIN_VERIFY_WORLD

from headless.events import WorldEvent
from headless.world import WorldSession
from headless.world.state import WorldState
from tests.mock.emitter import MemoryEmitter
from tests.mock.realm import MockRealm
from tests.mock.world import MockCharacter

logins_filename = os.environ.get('PONT_CREDS')
with open(logins_filename, 'r') as f:
	test_servers = json.load(f)

ac_login = test_servers['acore']['account']
client_world: Optional[WorldSession] = None

async def client_login(stream, session_key, nursery):
	realm = MockRealm(name='horse', address=('127.0.0.1', 123), num_characters=1, population=0, id=1)
	emitter = MemoryEmitter(nursery=nursery)
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
	assert 'headless.world.session.WorldSession._packet_handler' in str(world._parent_nursery.child_tasks)
	assert world._handling_packets

	# Test session state for logging in and entering the world
	assert WorldEvent.logging_in in emitter.memory
	assert WorldEvent.received_packet in emitter.memory
	assert WorldEvent.received_auth_response in emitter.memory
	assert WorldEvent.logged_in in emitter.memory

	async with world.enter_world(MockCharacter(name='Pont', guid=Guid(2))):
		assert WorldEvent.sent_player_login in world.emitter.memory
		assert WorldEvent.entered_world in world.emitter.memory
		packet = world.emitter.memory[WorldEvent.entered_world][0].kwargs['packet']

		assert packet.header.size == 22
		assert packet.map == 571
		assert packet.position == construct.Container(x=0, y=0, z=0)
		assert packet.rotation == 1.7999999523162842
		nursery.cancel_scope.cancel()


async def world_server(stream, session_key, nursery):
	stream = WorldServerStream(stream, session_key=session_key)
	await stream.send_unencrypted_packet(SMSG_AUTH_CHALLENGE, make_SMSG_AUTH_CHALLENGE(
		server_seed=7,
		encryption_seed1=31,
		encryption_seed2=71
	))

	# Sanity check that this is the same as how we sent it
	auth_session = await stream.receive_unencrypted_packet(CMSG_AUTH_SESSION)
	# assert auth_session.header.size == 309
	assert auth_session.build == 12340
	assert auth_session.login_server_id == 0

	assert auth_session.login_server_type == 0
	assert auth_session.client_seed == client_world._crypto.client_seed

	assert auth_session.region_id == 0
	assert auth_session.dos_response == 3
	assert auth_session.account_name == 'DINNERTABLE'
	assert auth_session.realm_id == 1

	await stream.send_encrypted_packet(SMSG_AUTH_RESPONSE, make_SMSG_AUTH_RESPONSE(AuthResponse.ok, Expansion.wotlk))

	login = await stream.receive_encrypted_packet(CMSG_PLAYER_LOGIN)
	assert login.guid == Guid(2)

	await stream.send_encrypted_packet(SMSG_LOGIN_VERIFY_WORLD, make_SMSG_LOGIN_VERIFY_WORLD(map=571, position=dict(x=0, y=0, z=0), rotation=1.8))

async def test_session():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	session_key = 887638991071640811242800621506026194914017482863646559938463468713468253926173117812986327918380

	with trio.fail_after(0.5):
		with pytest.raises(ProtocolError) as e:
			async with trio.open_nursery() as nursery:
				nursery.start_soon(client_login, client_stream, session_key, nursery)
				nursery.start_soon(world_server, server_stream, session_key, nursery)
		assert 'Packet handler stopped' in str(e)

async def test_session_wait_for():
	async with trio.open_nursery() as nursery:
		emitter = MemoryEmitter(emitter=pyee.TrioEventEmitter(nursery=nursery))

		async def emit_test():
			emitter.emit('test', arg1='arg', arg2=1)

		nursery.start_soon(emit_test)
		world = WorldSession(nursery=nursery, emitter=emitter)
		assert 'tests.world.test_session.test_session_wait_for.<locals>.emit_test' in str(nursery.child_tasks)

		with trio.fail_after(2):
			test = await world.wait_for_event(event='test')
			assert test == dict(arg1='arg', arg2=1)
			assert 'test' in emitter.memory
			print(emitter.memory['test'][0])

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
# 		async with world.enter_world(MockCharacter(name='Pont', guid=Guid(2))):
# 			await world.logout()
