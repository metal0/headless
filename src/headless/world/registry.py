from typing import Optional
from wlink import Guid

class Registry:
	pass

class RegistryQuery:
	def __init__(self, registry, name: Optional[str] = None, guid: Optional[Guid] = None):
		self.registry = registry
		self._name = name
		self._guid = guid

	@property
	def guid(self):
		return self._guid

	@property
	def name(self):
		return self._name