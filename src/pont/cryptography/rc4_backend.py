# TODO: Write last-resort RC4 Backend.
class RC4Backend:
	def __init__(self, key: bytes):
		self._key = key

	def encrypt(self, source: bytes) -> bytes:
		return source

