import trio
from pont_client.client import auth
from pont_client import cryptography
from pont_client.client.auth.errors import AuthError
from pont_client.utility.string import int_to_bytes

async def test_challenge_request():
	async def server(stream):
		salt = 13
		prime = 11
		generator = 7
		server_public = 31

		protocol = auth.AuthProtocol(stream=stream)
		challenge_request = await protocol.receive_challenge_request()
		await protocol.send_challenge_response(prime=prime, generator=generator, server_public=server_public, salt=salt)

		proof_request = await protocol.receive_proof_request()
		srp = cryptography.srp.WowSrpClient('user', 'pass', prime=prime, generator=generator)
		srp.compute_proof(salt=int_to_bytes(salt), server_public=server_public)
		await protocol.send_proof_response(session_proof_hash=srp.session_proof_hash)

	async def client(stream):
		protocol = auth.AuthProtocol(stream=stream)
		await protocol.send_challenge_request(username='user')
		challenge_response = await protocol.receive_challenge_response()

		(prime, salt, server_public, generator) = (
			challenge_response.prime, challenge_response.salt,
			challenge_response.server_public, challenge_response.generator
		)

		srp = cryptography.srp.WowSrpClient(username='user', password='pass', prime=prime, generator=generator)
		await protocol.send_proof_request(srp.client_public, srp.session_proof)

		proof_response = await protocol.receive_proof_response()
		if proof_response.session_proof_hash != srp.session_proof_hash:
			raise AuthError('Invalid username or password')

	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	async with trio.open_nursery() as n:
		n.start_soon(server, server_stream)
		n.start_soon(client, client_stream)