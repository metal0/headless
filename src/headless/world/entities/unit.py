from .object import Object
from headless.guid import Guid

class Unit(Object):
	def __init__(self, name: str, guid = Guid()):
		super().__init__(name, guid)

