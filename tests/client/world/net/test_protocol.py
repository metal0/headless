from typing import Optional

import trio

from pont.client.auth import Realm
from pont.client.world import Guid
from pont.client.world.entities.player import Race, Gender, CombatClass
from pont.client.world.expansions import Expansion
from pont.client.world.net import Opcode
from pont.client.world.net.packets.auth_packets import AuthResponse
from pont.client.world.net.protocol import WorldServerProtocol, WorldClientProtocol
from pont.client.world.session import WorldCrypto
from tests.client.cryptography import load_test_servers

logins_filename = '/home/fure/work/pont/servers_config.json'
test_servers = load_test_servers(logins_filename)
ac_login = test_servers['acore']['account']

client_crypto: Optional[WorldCrypto] = None

async def client_login(stream, session_key):
	async with trio.open_nursery() as nursery:
		realm = Realm.parse(Realm.build({
			'name': 'horse',
			'address': ('127.0.0.1', 123),
			'num_characters': 1,
			'population': 0,
		}))

		protocol = WorldClientProtocol(stream=stream, session_key=session_key)
		auth_challenge = await protocol.receive_SMSG_AUTH_CHALLENGE()
		assert auth_challenge.header.opcode == Opcode.SMSG_AUTH_CHALLENGE

		crypto = WorldCrypto(
			session_key,
			auth_challenge.server_seed,
			auth_challenge.encryption_seed1,
			auth_challenge.encryption_seed2
		)

		global client_crypto
		client_crypto = crypto

		await protocol.send_CMSG_AUTH_SESSION(
			account_name=ac_login['username'],
			client_seed=crypto.client_seed,
			account_hash=crypto.account_hash(ac_login['username']),
			realm_id=realm.id
		)

		auth_response = await protocol.receive_SMSG_AUTH_RESPONSE()
		assert auth_response.header.opcode == Opcode.SMSG_AUTH_RESPONSE

		# assert world._crypto.server_seed == 7
		# assert world._crypto.encryption_seed1 == 31
		# assert world._crypto.encryption_seed2 == 71

	# characters = await world.characters()

async def world_server(stream, session_key):
	protocol = WorldServerProtocol(stream, session_key=session_key)

	await protocol.send_SMSG_AUTH_CHALLENGE(
		server_seed=7,
		encryption_seed1=31,
		encryption_seed2=71
	)

	auth_session = await protocol.receive_CMSG_AUTH_SESSION()
	print(f'{auth_session=}')
	assert auth_session.header.size == 309
	assert auth_session.build == 12340
	assert auth_session.login_server_id == 0

	assert auth_session.login_server_type == 0
	assert auth_session.client_seed == client_crypto.client_seed

	assert auth_session.region_id == 0
	assert auth_session.dos_response == 3
	assert auth_session.account_name == ac_login['username'].upper()
	assert auth_session.realm_id == 1

	await protocol.send_SMSG_AUTH_RESPONSE(
		AuthResponse.ok, Expansion.wotlk
	)

async def test_protocol_parsing_decryption():
	with trio.fail_after(1):
		session_key = 887638991071640811242800621506026194914017482863646559938463468713468253926173117812986327918380
		(client_stream, server_stream) = trio.testing.memory_stream_pair()

		client = WorldClientProtocol(client_stream, session_key=session_key)
		await client.send_CMSG_AUTH_SESSION(ac_login['username'], 1, 2, 3)

		server = WorldServerProtocol(server_stream, session_key=session_key)
		auth_session = await server.receive_CMSG_AUTH_SESSION()

		assert auth_session.header.opcode == Opcode.CMSG_AUTH_SESSION
		assert auth_session.build == 12340
		assert auth_session.login_server_id == 0
		assert auth_session.account_name == ac_login['username'].upper()
		assert auth_session.client_seed == 1
		assert auth_session.account_hash == 2

		await client.send_CMSG_PING(id=10)
		ping = await server.receive_CMSG_PING()

		assert ping.header.size == 12
		assert ping.header.opcode == Opcode.CMSG_PING
		assert ping.id == 10
		assert ping.latency == 60

		addon_size = 0x7FFF
		addon_data = bytes([1] * addon_size)
		await server.send_SMSG_ADDON_INFO(data=addon_data)

		addon_info = await client.next_decrypted_packet()
		assert addon_info.header.size == addon_size + 2
		assert addon_info.header.opcode == Opcode.SMSG_ADDON_INFO
		assert addon_info.data == addon_data

		await server.send_SMSG_AUTH_RESPONSE(
			response=AuthResponse.ok,
			expansion=Expansion.wotlk,
			billing=dict(time_left=10),
			queue_position=None
		)

		auth_response = await client.next_decrypted_packet()
		assert auth_response.header.size == 13
		assert auth_response.header.opcode == Opcode.SMSG_AUTH_RESPONSE
		assert auth_response.response == AuthResponse.ok
		assert auth_response.billing.time_left == 10
		assert auth_response.billing.plan == 0
		assert auth_response.billing.time_rested == 0
		assert auth_response.queue_position is None

		await server.send_SMSG_NAME_QUERY_RESPONSE(
			guid=0, found=True,
			info=dict(
				name='Horse',
				realm_name='BigTown',
				race=Race.human, gender=Gender.male,
				combat_class=CombatClass.rogue,
			)
		)

		name_query = await client.next_decrypted_packet()
		assert name_query.header.size == 22
		assert name_query.header.opcode == Opcode.SMSG_NAME_QUERY_RESPONSE
		assert name_query.guid == Guid(0)
		assert name_query.found is True
		assert name_query.info.name == 'Horse'
		assert name_query.info.realm_name == 'BigTown'
		assert name_query.info.race == Race.human
		assert name_query.info.gender == Gender.male
		assert name_query.info.combat_class == CombatClass.rogue
		assert name_query.info.declined is False

# async def test_protocol():
# 	(client_stream, server_stream) = trio.testing.memory_stream_pair()
# 	session_key = 887638991071640811242800621506026194914017482863646559938463468713468253926173117812986327918380
#
	# with trio.fail_after(1):
	# 	async with trio.open_nursery() as nursery:
	# 		nursery.start_soon(client_login, client_stream, session_key)
	# 		nursery.start_soon(world_server, server_stream, session_key)