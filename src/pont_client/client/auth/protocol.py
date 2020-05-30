import trio

from .. import events, auth, log
log = log.get_logger(__name__)

class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._receiver_started = trio.Event()

	async def _receiver(self, emitter):
		self._receiver_started.set()
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
		nursery.start_soon(self._receiver)
		await receiver_started.wait()
		self.stream = stream

	async def send_login_challenge(self, username: str, country='enUS', arch='x86'):
		log.debug('Sending login challenge...')
		challenge = auth.packets.ChallengeRequest.build({
			'country': country,
			'architecture': arch,
			'account_name': username,
			'ip': self.stream._stream.socket.getsockname()[0]
		})

		await self.stream.send_all(challenge)

	async def receive_challenge_response(self) -> auth.packets.ChallengeResponse:
		data = await self.stream.receive_some()
		return auth.packets.parser.parse(data)

	async def send_proof_request(self, client_public, session_proof, checksum=0, num_keys=0, security_flags=0):
		proof_request = auth.packets.ProofRequest.build({
			'client_public': client_public,
			'session_proof': session_proof,
			'checksum': checksum,
			'num_keys': num_keys,
			'security_flags': security_flags
		})

		await self.stream.send_all(proof_request)

	async def receive_proof_response(self) -> auth.packets.ProofResponse:
		data = await self.stream.receive_some()
		return auth.packets.parser.parse(data)

	async def send_realmlist_request(self):
		await self.stream.send_all(auth.packets.RealmlistRequest.build())

	async def receive_realmlist_response(self) -> auth.packets.RealmlistResponse:
		data = await self.stream.receive_some()
		return auth.packets.parser.parse(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
		self._receiver_started = trio.Event()
