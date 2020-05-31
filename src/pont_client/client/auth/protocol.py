import trio

from .packets.constants import Response
from . import packets
from .. import events, log
log = log.get_logger(__name__)

class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._receiver_started = trio.Event()

	async def _receiver(self, receiver_started: trio.Event, emitter):
		receiver_started.set()
		emitter.emit(events.auth.connected, stream=self.stream)
		log.debug('receiver started')

		try:
			while True:
				data = await self.stream.receive_some()
				log.debug(f'received: {data=}')
				if not data:
					await self.stream.send_eof()
					emitter.emit(events.auth.disconnected, reason=f'EOF received')
					break
				emitter.emit(events.auth.data_received, data=data)

		except Exception as e:
			emitter.emit(events.auth.disconnected, reason=f'{e}')
			log.error(f'_receiver error: {e}')

	async def spawn_receiver(self, stream, nursery, emitter):
		receiver_started = trio.Event()
		nursery.start_soon(self._receiver, receiver_started, emitter)
		await receiver_started.wait()
		self.stream = stream

	async def send_challenge_request(self, username: str, country='enUS', arch='x86'):
		log.debug('Sending challenge request...')
		challenge = packets.ChallengeRequest.build({
			'country': country,
			'architecture': arch,
			'account_name': username,
			'ip': '10.179.204.114',
			'packet_size': 34 + len(username),
		})

		await self.stream.send_all(challenge)

	async def send_challenge_response(self, prime, server_public, salt, response: Response=Response.success,
			generator_length=1, generator=7, prime_length=32, checksum_salt=0, security_flag=0):
		log.debug('Sending challenge response...')
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

		await self.stream.send_all(challenge_response)

	async def receive_challenge_request(self) -> packets.ChallengeRequest:
		data = await self.stream.receive_some()
		return packets.ChallengeRequest.parse(data)

	async def receive_challenge_response(self) -> packets.ChallengeResponse:
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

		await self.stream.send_all(proof_request)

	async def send_proof_request(self, client_public, session_proof, checksum=0, num_keys=0, security_flags=0):
		proof_request = packets.ProofRequest.build({
			'client_public': client_public,
			'session_proof': session_proof,
			'checksum': checksum,
			'num_keys': num_keys,
			'security_flags': security_flags
		})

		await self.stream.send_all(proof_request)

	async def receive_proof_request(self) -> packets.ProofRequest:
		data = await self.stream.receive_some()
		return packets.ProofRequest.parse(data)

	async def receive_proof_response(self) -> packets.ProofResponse:
		data = await self.stream.receive_some()
		return packets.parser.parse(data)

	async def send_realmlist_request(self):
		await self.stream.send_all(packets.RealmlistRequest.build())

	async def receive_realmlist_request(self) -> packets.RealmlistRequest:
		data = await self.stream.receive_some()
		return packets.RealmlistRequest.parse(data)

	async def send_realmlist_response(self, realms):
		packets.RealmlistResponse.build({

			'num_realms': len(realms),
			'realms': realms,
		})

	async def receive_realmlist_response(self) -> packets.RealmlistResponse:
		data = await self.stream.receive_some()
		return packets.parser.parse(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
		self._receiver_started = trio.Event()
