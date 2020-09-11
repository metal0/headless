from typing import Optional, Tuple

import trio
from loguru import logger
from trio_socks import socks5

from pont.auth.net import AuthProtocol
from pont.client import events
from pont.utility.enum import ComparableEnum
from pont.utility.string import bytes_to_int
from .errors import InvalidLogin
from .. import cryptography


class AuthSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]]=None):
		self.proxy = proxy
		self.protocol: Optional[AuthProtocol] = None
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._srp: Optional[cryptography.WoWSrpClient] = None
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
			logger.info(f'Connecting to {address}...')

		elif stream is not None:
			logger.info(f'Using {stream} as auth stream.')

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
		logger.info('Connected!')

	async def authenticate(self, username, password, debug=None, country='enUS', arch='x86', os='OSX', build=12340):
		logger.info(f'Logging in with username {username}...')
		self._state = AuthState.logging_in
		self._username = username
		self._emitter.emit(events.auth.logging_in)

		await self.protocol.send_challenge_request(username=username, country=country, arch=arch, os=os, build=build)
		logger.debug('sent challenge request')

		challenge_response = await self.protocol.receive_challenge_response()
		logger.debug('received challenge response')

		client_private = debug['client_private'] if debug is not None else None
		self._srp = cryptography.WoWSrpClient(username=username, password=password,
		                                      prime=challenge_response.prime,
		                                      generator=challenge_response.generator,
		                                      client_private=client_private
		                                      )

		client_public, session_proof = self._srp.process(challenge_response.server_public, challenge_response.salt)
		self._session_key = int.from_bytes(self._srp.session_key, byteorder='little')
		logger.debug(f'{self._session_key=}')

		await self.protocol.send_proof_request(client_public=client_public, session_proof=session_proof)
		logger.debug('sent proof request')

		proof_response = await self.protocol.receive_proof_response()
		logger.debug('received proof response')

		logger.debug(f'{proof_response.session_proof_hash=} vs {self._srp.session_proof_hash:=}')

		if proof_response.session_proof_hash != self._srp.session_proof_hash:
			self._state = AuthState.disconnected
			self._emitter.emit(events.auth.invalid_login)
			self._emitter.emit(events.auth.disconnected, reason='Invalid login')
			raise InvalidLogin('Invalid username or password')

		self._state = AuthState.logged_in
		self._emitter.emit(events.auth.login_success)
		self._session_key = bytes_to_int(self._srp.session_key)
		logger.info(f'Logged in!')

	async def realms(self):
		await self.protocol.send_realmlist_request()
		result = await self.protocol.receive_realmlist_response()
		realmlist = list(result.realms)

		self._state = AuthState.realmlist_ready
		self._emitter.emit(events.auth.realmlist_ready, realmlist=realmlist)
		return realmlist

class AuthState(ComparableEnum):
	disconnected = -1
	not_connected = 0
	connected = 1
	logging_in = 2
	logged_in = 3
	realmlist_ready = 4