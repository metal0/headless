import trio
from loguru import logger

from . import packets, Opcode
from .packets import parse
from .response import Response
from ..realm import RealmFlags


class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()

	async def _send_all(self, data: bytes):
		async with self._send_lock:
			await self.stream.send_all(data)

	async def _receive_some(self, max_bytes=None):
		async with self._read_lock:
			return await self.stream.receive_some(max_bytes)

	async def send_challenge_request(self, username: str, build=12340, version='3.3.5', country='enUS', game='WoW', arch='x86', os='OSX', ip='127.0.0.1'):
		await self._send_all(packets.ChallengeRequest.build(dict(
			country=country,
			build=build,
			version=version,
			game=game,
			architecture=arch,
			account_name=username,
			ip=ip,
			os=os,
			size=30 + len(username),
		)))

	async def send_challenge_response(self, prime: int, server_public: int, salt: int, response: Response=Response.success,
			generator_length=1, generator=7, prime_length=32, checksum=0, security_flag=0):
		await self._send_all(packets.ChallengeResponse.build({
			'server_public': server_public,
			'response': response,
			'generator_length': generator_length,
			'generator': generator,
			'prime_length': prime_length,
			'prime': prime,
			'salt': salt,
			'checksum': checksum,
			'security_flag': security_flag
		}))

	async def receive_challenge_request(self) -> packets.ChallengeRequest:
		data = await self._receive_some()
		return packets.ChallengeRequest.parse(data)

	async def receive_challenge_response(self) -> packets.ChallengeResponse:
		data = await self._receive_some()
		return packets.parser.parse(data)

	async def send_proof_response(self, response: Response, session_proof_hash: int=0, account_flags=32768, survey_id=0, login_flags=0):
		await self._send_all(packets.ProofResponse.build(dict(
			header=dict(response=response),
			session_proof_hash=session_proof_hash,
			account_flags=account_flags,
			survey_id=survey_id,
			login_flags=login_flags
		)))

	async def send_proof_request(self, client_public: int, session_proof: int, checksum: int=4601254584545541958749308449812234986282924510, num_keys: int=0, security_flags: int=0):
		await self._send_all(packets.ProofRequest.build({
			'client_public': client_public,
			'session_proof': session_proof,
			'checksum': checksum,
			'num_keys': num_keys,
			'security_flags': security_flags
		}))

	async def receive_proof_request(self) -> packets.ProofRequest:
		data = await self._receive_some()
		return packets.ProofRequest.parse(data)

	async def receive(self, expected_size: int):
		data = bytearray()
		while expected_size > 0:
			data += await self._receive_some(expected_size)
			expected_size -= len(data)

		return bytes(data)

	async def receive_proof_response(self) -> packets.ProofResponse:
		data = await self._receive_some()
		return packets.parser.parse(data)

	async def send_realmlist_request(self):
		packet = packets.RealmlistRequest.build({})
		await self._send_all(packet)

	async def receive_realmlist_request(self) -> packets.RealmlistRequest:
		data = await self._receive_some()
		return packets.RealmlistRequest.parse(data)

	async def send_realmlist_response(self, realms):
		size = 8
		for realm in realms:
			size += 3 + len(realm['name']) + 1 + len(':'.join(map(str, realm['address']))) + 1 + 4 + 3
			if 'flags' in realm and (realm['flags'] & RealmFlags.specify_build) == RealmFlags.specify_build.value:
				size += 5

		await self._send_all(packets.RealmlistResponse.build({
			'realms': realms,
			'size': size
		}) + b'\x10\x00')

	async def receive_realmlist_response(self) -> packets.RealmlistResponse:
		data = await self._receive_some()
		return packets.parser.parse(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
