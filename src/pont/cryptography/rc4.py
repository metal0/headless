from loguru import logger

__all__ = ['RC4']

# noinspection PyPackageRequirements
def import_arc4_backend():
	import arc4
	# logger.debug('arc4 library backend selected')
	return lambda key: lambda data: arc4.ARC4(key).encrypt(data)

def import_cryptography_backend():
	from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
	from cryptography.hazmat.backends import default_backend
	def create_encryptor(key):
		encryptor = Cipher(algorithms.ARC4(key), backend=default_backend(), mode=None).encryptor()
		def encrypt(data: bytes):
			return encryptor.update(data)

		return encrypt
	# logger.debug('cryptography.io library backend selected')
	return create_encryptor

backends = [import_arc4_backend, import_cryptography_backend]
backend_encrypt = None

for import_backend in backends:
	try:
		backend_encrypt = import_backend()
		break

	except (ImportError, ModuleNotFoundError):
		pass

if backend_encrypt is None:
	raise ImportError('No supported RC4 encryption module found')

class RC4:
	def __init__(self, key):
		self.key = key
		self._encrypt = backend_encrypt(key)

	def encrypt(self, data):
		return self._encrypt(data)

	def decrypt(self, data):
		return self._encrypt(data)
