import traceback

import trio

from tests.client.cryptography import load_test_servers

logins_filename = 'C:/Users/dinne/Documents/Projects/pont/servers_config.json'
test_servers = load_test_servers(logins_filename)
ac_login = test_servers['acore']['account']

async def client_login(auth_address, stream):
	try:
		session_key = 0
		protocol = pont.world.net.WorldProtocol(stream)
		auth_challenge = await protocol.receive_SMSG_AUTH_CHALLENGE()

		assert auth_challenge.server_seed == 7
		assert auth_challenge.encryption_seed1 == 31
		assert auth_challenge.encryption_seed1 == 73

	except:
		traceback.print_exc()

async def world_server(stream):
	try:
		protocol = pont.world.net.WorldProtocol(stream)
		await protocol.send_SMSG_AUTH_CHALLENGE(
			server_seed=7,
			encryption_seed1=31,
			encryption_seed2=71
		)

		# auth_session = await protocol.receive_CMSG_AUTH_SESSION()

	except:
		traceback.print_exc()

async def test_auth_protocol():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	auth_address = ('10.179.205.114', 3724)
	with trio.fail_after(1):
		async with trio.open_nursery() as nursery:
			nursery.start_soon(client_login, auth_address, client_stream)
			nursery.start_soon(world_server, server_stream)