from contextlib import asynccontextmanager, AsyncExitStack
from typing import Tuple, Optional

import trio
import pyee
from enum import Enum

from . import log, Config
from .auth import AuthSession
from .world.session import WorldSession
from ..utility import AsyncScopedEmitter, enum

log = log.get_logger(__name__)

class ClientState(enum.ComparableEnum):
	not_connected = 1
	connected = 2
	logging_in = 3
	logged_in = 4
	realmlist = 5
	character_select = 6
	loading_world = 7
	in_game = 8

@asynccontextmanager
async def _open_nursery():
	nursery = trio.open_nursery()
	try:
		yield nursery
	finally:
		nursery.cancel_scope.cancel()

# TODO: Figure out how to context-manage a nursery
class Client(AsyncScopedEmitter):
	def __init__(self, proxy=None):
		super().__init__(emitter=None)
		self._reset(proxy)
		self.config = Config(
			relogger=False,
			emitter=self
		)

	def _reset(self, proxy=None):
		self._proxy = proxy
		self._state = ClientState.not_connected
		self.auth = None
		self.world = None
		self.framerate = 60

	async def __aenter__(self):
		await super().__aenter__()
		self.nursery = await trio.open_nursery()

		# self.nursery = await self._nursery_mgr.__aenter__()
		self._emitter = pyee.TrioEventEmitter(nursery=self.nursery)
		self.auth = AuthSession(nursery=self.nursery, emitter=self, proxy=self._proxy)
		self.world = WorldSession(nursery=self.nursery, emitter=self, proxy=self._proxy)
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await super().__aexit__(exc_type, exc_val, exc_tb)
		if self.auth is not None:
			await self.auth.aclose()

		if self.world is not None:
			await self.world.aclose()

		self._reset()
		self.nursery.cancel_scope.cancel()

	async def aclose(self):
		if self.auth is not None:
			await self.auth.aclose()

		if self.world is not None:
			await self.world.aclose()

		await trio.lowlevel.checkpoint()
		self._reset()
		self.nursery.cancel_scope.cancel()
		await super().aclose()

	async def login(self, username: str, password: str, address: Tuple[str, int], proxy: Optional[Tuple[str, int]]=None):
		await self.auth.connect(address, proxy=proxy)
		await self.auth.authenticate(username=username, password=password)

	@property
	def state(self) -> ClientState:
		return self._state

	def is_at_character_select(self):
		return self.state == ClientState.character_select

	def is_loading(self):
		return self.state == ClientState.loading_world

	def is_logging_in(self):
		return self.state == ClientState.logging_in

	def is_logged_in(self):
		return self.state >= ClientState.logged_in

	def is_ingame(self):
		return self.state == ClientState.in_game

	def is_connected(self):
		return self.state != ClientState.not_connected
