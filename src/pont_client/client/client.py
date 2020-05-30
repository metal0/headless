import trio
import pyee
from enum import Enum

from . import log, Config
from .state import ClientState
from .auth import AuthSession
from ..utility import AsyncScopedEmitter

log = log.get_logger(__name__)

class ClientState(Enum):
	not_connected = 1
	logging_in = 2
	realmlist = 3
	character_select = 4
	loading_world = 5
	in_game = 6

class Client(AsyncScopedEmitter):
	def __init__(self, proxy=None):
		self.nursery = trio.open_nursery()
		emitter = pyee.TrioEventEmitter(nursery=self.nursery)
		super().__init__(emitter=emitter)
		self._proxy = proxy
		self._reset(proxy)
		self.framerate = 60
		self.config = Config(
			relogger=False,
			emitter=self
		)

	def _reset(self, proxy=None):
		self._proxy = proxy
		self._state = ClientState.not_connected
		self.auth = AuthSession(nursery=self.nursery, emitter=self, proxy=proxy)
		self.world = None

	def _update_auth_info(self, username: str = None, password: str = None, realm_name: str = None):
		if username is not None:
			self.config.username = username
		if password is not None:
			self.config.password = password
		if realm_name is not None:
			self.config.realm_name = realm_name

	async def __aenter__(self):
		await super().__aenter__()
		await self.nursery.__aenter__()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await super().__aexit__(exc_type, exc_val, exc_tb)
		await self.aclose()
		await self.nursery.__aexit__(exc_type, exc_val, exc_tb)

	async def aclose(self):
		if self.auth is not None:
			await self.auth.aclose()
			await trio.lowlevel.checkpoint()

		if self.world is not None:
			await self.world.aclose()
			await trio.lowlevel.checkpoint()

		self._reset()
		await super().aclose()

	@property
	def state(self) -> ClientState:
		return self._state

	def is_at_character_select(self):
		return False

	def is_ingame(self):
		return False

	def is_connected(self):
		return False
