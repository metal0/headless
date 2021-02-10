import trio
import pont
from examples.chatbot.plugin import Plugin, PluginManager
from pont.client.log import logger
from pont.client import world, auth
from typing import Tuple, Optional, List

class Chatbot:
	def __init__(self, character: str, realm: str, realmlist: Tuple[str, int], plugins: List[Plugin]):
		self._character_name = character
		self._realm_name = realm
		self._realmlist = realmlist
		self._plugin_manager = PluginManager()
		self._plugins = plugins

		self.nursery = None
		self.client: Optional[pont.Client] = None

	@property
	def realmlist(self):
		return self._realmlist

	@property
	def character(self) -> str:
		return self._character_name

	@property
	def realm(self) -> str:
		return self._realm_name

	def on(self, *args, **kwargs):
		return self.client.on(*args, **kwargs)

	def plugin(self, plugin_type):
		return self._plugin_manager.reference(plugin_type)

	def load_plugin(self, plugin):
		try:
			# Recursively load all plugin requirements first
			for requirement in plugin.requirements:
				self.load_plugin(requirement)

			# Finally load desired plugin
			self._plugin_manager.load(plugin, bot=self)
		except Exception as e:
			logger.exception(e)

	def attach(self, client):
		self.client = client
		self.nursery = client.nursery

		for plugin in self._plugins:
			self.load_plugin(plugin)

	async def run(self, username: str, password: str, proxy=None):
		try:
			client: pont.Client
			async with pont.open_client(auth_server=self._realmlist, proxy=proxy) as client:
				self.attach(client)

				# Login to auth server
				with trio.fail_after(5):
					await client.login(username, password)

				# Find desired realm
				for realm in await client.realms():
					if realm.name == self._realm_name:
						break

				# Connect to the world server
				with trio.fail_after(5):
					await client.select_realm(realm)

				# Find desired character
				for character in await client.characters():
					if character.name == self._character_name:
						break

				while True:
					# Enter world with character
					async with client.enter_world(character):
						await trio.sleep_forever()

					await trio.sleep(2)

		except (Exception, trio.TooSlowError, auth.AuthError, world.WorldError):
			logger.exception('Error')

