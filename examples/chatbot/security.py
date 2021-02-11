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

class AccessList(AccessControl):
	def __init__(self, *controls):
		self._controls = []
		for control in controls:
			self.add(control)

	async def authenticate(self, identity):
		for control in self._controls:
			if await control.authenticate(identity):
				return True
		return False

	def add(self, control):
		self._controls.append(control)
