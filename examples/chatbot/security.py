import abc

class AccessControl(abc.ABC):
	async def authenticate(self, identity):
		raise NotImplemented()

class Identity:
	def __init__(self, guid):
		self._guid = guid

	@property
	def guid(self):
		return self._guid

class AccessList:
	def __init__(self, *controls):
		self._controls = []
		for control in controls:
			self.add(control)

	def add(self, control):
		self._controls.append(control)