class RC4:
	sbox_length = 256

	@staticmethod
	def _create_sbox(key: bytes) -> bytes:
		sbox = list(range(0, RC4.sbox_length))
		j = 0

		for i in range(0, RC4.sbox_length):
			j = (j + sbox[i] + key[i % len(key)] + RC4.sbox_length) % RC4.sbox_length
			sbox[i], sbox[j] = sbox[j], sbox[i]

		return bytearray(sbox)

	def encrypt(self, data) -> bytes:
		encrypted = bytearray([0]*len(data))
		for n in range(0, len(data)):
			self._i = (self._i + 1) % RC4.sbox_length
			self._j = (self._j + self._sbox[self._i]) % RC4.sbox_length
			i, j = self._i, self._j

			self._sbox[i], self._sbox[j] = self._sbox[j], self._sbox[i]
			rand = self._sbox[(self._sbox[i] + self._sbox[j]) % RC4.sbox_length]
			encrypted[n] = (rand ^ data[n])

		return bytes(encrypted)

	def __init__(self, key: bytes):
		self._key = key
		self._sbox = RC4._create_sbox(key)
		self._i = 0
		self._j = 0
