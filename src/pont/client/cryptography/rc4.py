class RC4:
	def __init__(self, key):
		self.key = key

		try:
			import arc4
			self._encrypt = lambda data: arc4.ARC4(self.key).encrypt(data)
		except ImportError:
			import rc4
			self._encrypt = lambda data: rc4.rc4(data, self.key)

	def encrypt(self, data):
		return self._encrypt(data)
