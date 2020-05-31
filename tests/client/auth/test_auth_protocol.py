import trio
from pont_client import client as pont
from pont_client.client import auth

async def auth_server(stream):
	protocol = auth.AuthProtocol(stream)
	challenge_request = await protocol.receive_challenge_request()

	assert challenge_request.packet_size == 34 + len(challenge_request.account_name)
	assert challenge_request.game == 'WoW'
	assert challenge_request.version == [3, 3, 5]
	assert challenge_request.build == 12340

	await protocol.send_challenge_response(prime=7, server_public=37, salt=67)

async def client_login(auth_address, stream):
	async with pont.Client() as client:
		try:
			await client.auth.connect(auth_address, stream=stream)
			await client.auth.authenticate('user', 'pass')
			#
			# realmlist = await client.auth.realmlist()
			# for realm in realmlist:
			# 	if realm.name == 'AzerothCore':
			# 		ac = realm
			#
			# await client.world.connect(ac, client.auth)
			# characters = await client.world.characters()

			# await client.enter_world(characters[0], on_client_tick)

		except Exception as e:
			print(e)

async def test_auth_protocol():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	auth_address = ('10.179.205.114', 3724)
	async with trio.open_nursery() as nursery:
		nursery.start_soon(client_login, auth_address, client_stream)
		nursery.start_soon(auth_server, server_stream)