import trio

from pont.client.auth.net import packets
from .response import Response
from loguru import logger

class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()

	async def send_challenge_request(self, username: str, build=12340, country='enUS', game='WoW', arch='x86', os='Win', ip='127.0.0.1'):
		logger.debug('Sending challenge request...')
		packet = packets.ChallengeRequest.build({
			'country': country,
			'build': build,
			'game': game,
			'architecture': arch,
			'account_name': username,
			'ip': ip,
			'os': os,
			'packet_size': 30 + len(username),
		})
		async with self._send_lock:
			await self.stream.send_all(packet)

	async def send_challenge_response(self, prime, server_public, salt, response: Response=Response.success,
			generator_length=1, generator=7, prime_length=32, checksum_salt=0, security_flag=0):
		logger.debug('Sending challenge response...')
		challenge_response = packets.ChallengeResponse.build({
			'server_public': server_public,
			'response': response,
			'generator_length': generator_length,
			'generator': generator,
			'prime_length': prime_length,
			'prime': prime,
			'salt': salt,
			'checksum_salt': checksum_salt,
			'security_flag': security_flag
		})
		async with self._send_lock:
			await self.stream.send_all(challenge_response)

	async def receive_challenge_request(self) -> packets.ChallengeRequest:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.ChallengeRequest.parse(data)

	async def receive_challenge_response(self) -> packets.ChallengeResponse:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.parser.parse(data)

	async def send_proof_response(self, session_proof_hash, response: Response=Response.success, account_flags=32768, survey_id=0, login_flags=0):
		proof_request = packets.ProofResponse.build({
			'response': response,
			'session_proof_hash': session_proof_hash,
			'account_flags': account_flags,
			'survey_id': survey_id,
			'login_flags': login_flags
		})
		async with self._send_lock:
			await self.stream.send_all(proof_request)

	async def send_proof_request(self, client_public: int, session_proof: int, checksum: int=0, num_keys: int=0, security_flags: int=0):
		proof_request = packets.ProofRequest.build({
			'client_public': client_public,
			'session_proof': session_proof,
			'checksum': checksum,
			'num_keys': num_keys,
			'security_flags': security_flags
		})

		async with self._send_lock:
			await self.stream.send_all(proof_request)

	async def receive_proof_request(self) -> packets.ProofRequest:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.ProofRequest.parse(data)

	async def receive_proof_response(self) -> packets.ProofResponse:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.parser.parse(data)

	async def send_realmlist_request(self):
		async with self._send_lock:
			packet = packets.RealmlistRequest.build({})
			await self.stream.send_all(packet)

	async def receive_realmlist_request(self) -> packets.RealmlistRequest:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.RealmlistRequest.parse(data)

	async def send_realmlist_response(self, realms):
		async with self._send_lock:
			packet = packets.RealmlistResponse.build({
				'realms': realms,
			})

			await self.stream.send_all(packet)

	async def receive_realmlist_response(self) -> packets.RealmlistResponse:
		async with self._read_lock:
			data = await self.stream.receive_some()
			return packets.parser.parse(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
