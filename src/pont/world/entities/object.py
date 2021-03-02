from pont.world import Guid

class Object:
	def __init__(self, name: str, guid = Guid()):
		self.__guid = guid
		self.__name = name

	def guid(self) -> Guid:
		return self.__guid

	def name(self) -> str:
		return self.__name