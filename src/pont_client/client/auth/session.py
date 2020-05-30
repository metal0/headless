import trio
from trio_socks import socks5
from typing import Optional, Tuple

from .errors import AuthError
from .protocol import AuthProtocol
from .. import log, auth
from ... import cryptography

log = log.get_logger(__name__)

class AuthSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]]=None):
		self.proxy = proxy
		self.protocol = AuthProtocol(stream=self._stream)
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._srp: Optional[cryptography.srp.WowSrpClient] = None
		self.__session_key = None

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()

	async def connect(self, auth_server_address, proxy=None, stream=None):
		if stream is None:
			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(destination=auth_server_address, proxy=proxy or self.proxy)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*auth_server_address)
		else:
			self._stream = stream

		await self.protocol.spawn_receiver(self._stream, nursery=self._nursery, emitter=self._emitter)

	async def authenticate(self, username, password):
		await self.protocol.send_login_challenge(username=username)
		challenge_response = await self.protocol.receive_challenge_response()
		self._srp = cryptography.srp.WowSrpClient(username=username, password=password,
		    prime=challenge_response.prime,
			generator=challenge_response.generator,
		)

		self._srp.process(challenge_response.server_public, challenge_response.salt)
		self.__session_key = self._srp.session_key

		await self.protocol.send_proof_request(client_public=self._srp.client_public, session_proof=self._srp.session_proof)
		proof_response = await self.protocol.receive_proof_response()
		if proof_response.session_proof_hash != self._srp.session_proof_hash:
			raise AuthError('Invalid username or password')

	async def realmlist(self):
		await self.protocol.send_realmlist_request()
		return await self.protocol.receive_realmlist_response()
