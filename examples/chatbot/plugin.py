from abc import ABC

from wlink.log import logger

class Plugin(ABC):
	requirements = []

	def check_requirements(self, bot) -> bool:
		for requirement in self.requirements:
			if bot.plugin(requirement) is None:
				return False

		return True

	def load(self, bot):
		raise NotImplemented()

class PluginManager:
	def __init__(self):
		self._plugins = []

	def load(self, plugin, bot):
		# If plugin_type refers to an actual plugin object
		if not issubclass(type(plugin), Plugin):
			return

		if plugin not in self._plugins:
			try:
				plugin.load(bot)
				self._plugins.append(plugin)

			except TypeError as e:
				logger.exception(f'Error loading {plugin}: {e}')

	def remove(self, plugin_type):
		# If plugin_type refers to an actual plugin object
		if issubclass(type(plugin_type), Plugin):
			plugin_type = type(plugin_type)

		i = None
		for i in range(len(self._plugins)):
			if type(self._plugins[i]) == plugin_type:
				break

		if i is not None:
			self._plugins[i].unload()
			self._plugins.pop(i)

	def reference(self, plugin_type):
		# If plugin_type refers to an actual plugin object
		if issubclass(type(plugin_type), Plugin):
			plugin_type = type(plugin_type)

		for plugin in self._plugins:
			if type(plugin) == plugin_type:
				return plugin

		return None
