from contextlib import asynccontextmanager
from typing import Tuple

import pyee
import trio

from pont.client.auth import AuthSession, Realm
from pont.client.auth.session import AuthState
from pont.client.world import WorldSession
from pont.client.world.character import CharacterInfo
from pont.client.world.state import WorldState
from .config import Config
from . import auth, world
from ..utility import AsyncScopedEmitter, enum


@asynccontextmanager
async def open_client(auth_server=None, proxy=None):
	'''
	Creates a client bound to the given auth server, with the choice to connect through a SOCKS proxy server.
	:param auth_server: the address of the auth server to connect to.
	:param proxy: address of the proxy server to use.
	:return: an unconnected Client
	'''
	async with trio.open_nursery() as nursery:
		client = Client(nursery, auth_server=auth_server, proxy=proxy)
		try:
			async with client:
				yield client
			nursery.cancel_scope.cancel()
		finally:
			await client.aclose()

class ClientState(enum.ComparableEnum):
	not_connected = 1
	connected = 2
	logging_in = 3
	logged_in = 4
	realmlist = 5
	character_select = 6
	loading_world = 7
	in_game = 8

class Client(AsyncScopedEmitter):
	def __init__(self, nursery, auth_server: Tuple[str, int], proxy=None):
		super().__init__(emitter=pyee.TrioEventEmitter(nursery=nursery))
		self._auth_server_address = auth_server
		self._proxy = proxy
		self._username = None
		self._reset()
		self.config = Config(
			emitter=self,
			relogger=False,
			# log='./pont.log',
		)

		self.nursery = nursery
		self.auth = AuthSession(nursery=self.nursery, emitter=self, proxy=self._proxy)
		self.world = WorldSession(nursery=self.nursery, emitter=self, proxy=self._proxy)

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if self.world.state >= WorldState.in_game:
			await self.logout()

		await super().__aexit__(exc_type, exc_val, exc_tb)

	@property
	def auth_server_address(self):
		return self._auth_server_address

	@auth_server_address.setter
	def auth_server_address(self, other: Tuple[str, int]):
		if self.auth.state > AuthState.not_connected:
			raise auth.ProtocolError('Already connected to an auth server')

		self._auth_server_address = other

	def _reset(self):
		self._state = ClientState.not_connected
		self._session_key = None
		self._username = None
		self.auth = None
		self.world = None
		self.framerate = 60

	async def aclose(self):
		if self.auth is not None:
			await self.auth.aclose()

		if self.world is not None:
			await self.world.aclose()

		await trio.lowlevel.checkpoint()

		self._reset()
		await super().aclose()

	async def login(self, username: str, password: str, country: str='enUS', arch: str='x86', os: str='OSX', build: int=12340):
		'''
		Connect to the auth server and then authenticate using the given username and password.
		:param os: The operating system string to send to the auth server
		:param build: The game build to send
		:param arch: The architecture of the game (x86 or x64)
		:param country: The localization (e.g. enUS)
		:param username: username to use.
		:param password: password to use.
		:return: None
		'''
		self._username = username
		if self.auth.state < AuthState.connected:
			await self.auth.connect(self._auth_server_address, proxy=self._proxy)

		await self.auth.authenticate(username=username, password=password)

	async def realms(self):
		if self.auth.state < AuthState.logged_in:
			raise auth.ProtocolError('Not logged in')

		return await self.auth.realms()

	async def select_realm(self, realm: Realm):
		if self.world.state > WorldState.connected:
			raise world.ProtocolError('Already connected to a realm')

		if self.auth.session_key is None:
			raise auth.AuthError('Invalid session key')

		await self.world.connect(realm, proxy=self._proxy)
		await self.world.authenticate(self._username, self.auth.session_key)

	async def characters(self):
		if self.world.state < WorldState.logged_in:
			raise world.ProtocolError('Not logged in')

		return await self.world.characters()

	@asynccontextmanager
	def enter_world(self, character: CharacterInfo):
		if self.world.state < WorldState.logged_in:
			raise world.ProtocolError('Not logged in')
		return self.world.enter_world(character).gen

	async def logout(self):
		await self.world.logout()

	@property
	def state(self) -> ClientState:
		return self._state

	def is_at_character_select(self):
		return self.world.state >= WorldState.logged_in

	def is_loading(self):
		return self.world.state == WorldState.loading

	def is_logging_in(self):
		return self.state == WorldState.logging_in

	def is_logged_in(self):
		return self.auth.state >= AuthState.logged_in

	def is_ingame(self):
		return self.world.state >= WorldState.in_game

__all__ = [Client, ClientState, open_client, ]