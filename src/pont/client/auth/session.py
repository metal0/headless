from typing import Optional, Tuple

import trio
from trio_socks import socks5

from pont.client.auth.net.protocol import AuthProtocol
from .errors import AuthError
from .state import AuthState
from .. import log, events, cryptography
from ...utility.string import bytes_to_int

log = log.mgr.get_logger(__name__)

class AuthSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]]=None):
		self.proxy = proxy
		self.protocol: Optional[AuthProtocol] = None
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._srp: Optional[cryptography.WowSrpClient] = None
		self._session_key = None
		self._username = None
		self._state = AuthState.not_connected

	@property
	def state(self):
		return self._state

	@property
	def session_key(self):
		return self._session_key

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()
			self._stream = None

		self._state = AuthState.not_connected

	async def connect(self, address=None, proxy=None, stream=None):
		if address is not None:
			if type(address) == str:
				address = (address, 3724)
			log.info(f'Connecting to {address}...')

		elif stream is not None:
			log.info(f'Using {stream} as auth stream.')

		if stream is None:
			if address is None:
				raise ValueError('Both stream and address cannot be None!')

			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(destination=address, proxy=proxy or self.proxy or None)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*address)
		else:
			self._stream = stream

		self.protocol = AuthProtocol(stream=self._stream)
		self._state = AuthState.connected
		self._emitter.emit(events.auth.connected)
		log.info('Connected!')

	async def authenticate(self, username, password, debug=None):
		log.info(f'Logging in with username {username}...')
		self._state = AuthState.logging_in
		self._username = username
		self._emitter.emit(events.auth.logging_in)

		await self.protocol.send_challenge_request(username=username, os='OSX')
		log.debug('sent challenge request')

		challenge_response = await self.protocol.receive_challenge_response()
		log.debug('received challenge response')

		client_private = None
		if debug:
			client_private = debug['client_private']

		self._srp = cryptography.WowSrpClient(username=username, password=password,
		                                                      prime=challenge_response.prime,
		                                                      generator=challenge_response.generator,
		                                                      client_private=client_private
		                                                      )

		client_public, session_proof = self._srp.process(challenge_response.server_public, challenge_response.salt)
		self._session_key = int.from_bytes(self._srp.session_key, byteorder='little')
		log.debug(f'{self._session_key=}')

		await self.protocol.send_proof_request(client_public=client_public, session_proof=session_proof)
		log.debug('sent proof request')

		proof_response = await self.protocol.receive_proof_response()
		log.debug('received proof response')

		log.debug(f'{proof_response.session_proof_hash=} vs {self._srp.session_proof_hash:=}')

		if proof_response.session_proof_hash != self._srp.session_proof_hash:
			self._state = AuthState.disconnected
			self._emitter.emit(events.auth.invalid_login)
			self._emitter.emit(events.auth.disconnected, reason='Invalid login')
			raise AuthError('Invalid username or password')

		self._state = AuthState.logged_in
		self._emitter.emit(events.auth.login_success)
		self._session_key = bytes_to_int(self._srp.session_key)
		log.info(f'Logged in!')

	async def realmlist(self):
		await self.protocol.send_realmlist_request()
		result = await self.protocol.receive_realmlist_response()
		realmlist = list(result.realms)

		self._state = AuthState.realmlist_ready
		self._emitter.emit(events.auth.realmlist_ready, realmlist=realmlist)
		return realmlist
