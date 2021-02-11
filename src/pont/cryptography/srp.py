import os
import random
from typing import Tuple, Optional

from loguru import logger

from pont.client.auth.errors import InvalidLogin
from pont.utility.string import int_to_bytes, bytes_to_int
from .sha import sha1, sha1v

default_prime = 62100066509156017342069496140902949863249758336000796928566441170293728648119
default_generator = 7
default_multiplier = 3

class SrpError(Exception):
	pass

def sha_interleave(value: int) -> bytes:
	t = int_to_bytes(value)

	t1 = []
	for i in range(0, 32, 2):
		t1.append(t[i])

	sha = sha1(t1)
	result = list(range(0, 40))

	# fill even result entries [0], [2] etc.
	for i in range(0, 20):
		result[i * 2] = sha[i]

	try:
		for i in range(0, 16):
			if (i * 2 + 1) >= len(t):
				t1[i] = 0
			else:
				t1[i] = t[i * 2 + 1]

		sha = sha1(t1)
		# fill uneven result entries [1], [3] etc.
		for i in range(0, 20):
			result[i * 2 + 1] = sha[i]
	except Exception as e:
		logger.debug(f'{len(t1)=} {i=} {t=}')
		logger.exception('Weird srp error')
		raise SrpError(e)

	return bytes(result)

class WoWSrp:
	def __init__(self,
		username: str, password: str,
		prime: Optional[int]=None,
		generator: int=7,
		multiplier: int=3,
	):
		self.prime = prime if prime is not None else default_prime
		self.generator = generator if generator is not None else default_generator
		self.multiplier = multiplier if multiplier else default_multiplier

		self.session_key = None
		self.session_proof = None
		self.session_proof_hash = None
		self.common_secret = None

		self._username = username.upper()
		self._password = password.upper()

	def compute_proof(self, session_key: int, salt: int, server_public: int, client_public: int) -> Tuple[int, int]:
		N_sha = sha1(self.prime, out=int)
		g_sha = sha1(self.generator, out=int)

		# calculate M1
		session_proof = sha1(
			N_sha ^ g_sha,
			sha1(self._username),
			salt,
			client_public,
			server_public,
			session_key
		)

		hash = sha1(client_public, session_proof, session_key)
		return bytes_to_int(session_proof), bytes_to_int(hash)

class WoWSrpServer(WoWSrp):
	def __init__(self,
	    username: str, password: str,
	    prime: Optional[int]=None, generator: int=7,
		salt: int=random.getrandbits(1024), server_private: int=random.getrandbits(1024)
	):
		super().__init__(username, password, prime, generator)
		self.server_private = server_private
		self.salt = salt

		prehash = sha1(f'{username}:{password}')
		self.password_hash = sha1(salt, prehash, out=int)
		self.password_verifier = pow(self.generator, self.password_hash, self.prime)
		self.server_public = ((self.multiplier * self.password_verifier) + pow(self.generator, server_private, self.prime)) % self.prime

		if self.server_public == 0:
			raise SrpError('server_public must not be zero')

		self._server_premaster_secret = None

	def process(self, session_proof: int, client_public: int):
		self.common_secret = sha1(client_public, self.server_public, out=int)
		self._server_premaster_secret = pow((client_public * pow(self.password_verifier, self.common_secret, self.prime)), self.server_private, self.prime)

		self.session_key = sha_interleave(self._server_premaster_secret)
		self.session_proof, self.session_proof_hash = self.compute_proof(bytes_to_int(self.session_key), self.salt, self.server_public, client_public)
		return self.session_key, self.session_proof

class WoWSrpClient(WoWSrp):
	def __init__(self, username: str, password: str, prime: int, generator: int, client_private=None):
		super().__init__(username, password, prime, generator)
		self.client_private = random.getrandbits(1024) if client_private is None else client_private

		self.client_public = pow(self.generator, self.client_private, self.prime)
		if self.client_public == 0:
			raise InvalidLogin('client_public must not be zero')

		self.password_hash = 0
		self.password_verifier = 0
		self.client_premaster_secret = 0

	def process(self, server_public: int, salt: int) -> Tuple[int, int]:
		"""Returns: client_public, session_proof"""
		prehash = sha1(f'{self._username}:{self._password}')
		self.password_hash = sha1(salt, prehash, out=int)
		self.password_verifier = pow(self.generator, self.password_hash, self.prime)
		self.common_secret = sha1(self.client_public, server_public, out=int)

		# this is S
		self.client_premaster_secret = pow(
			(server_public - (self.multiplier * self.password_verifier)),
			(self.client_private + (self.common_secret * self.password_hash)), self.prime)

		# this is K
		self.session_key = sha_interleave(self.client_premaster_secret)
		self.session_proof, self.session_proof_hash = self.compute_proof(bytes_to_int(self.session_key), salt=salt, server_public=server_public, client_public=self.client_public)
		return bytes_to_int(self.client_public), self.session_proof

class SrpChecksumNoGameFiles(Exception):
	pass

def generate_crc(client_public, crc_salt: int, game_files_root: str = 'C:\\Users\\dinne\\Downloads\\World of Warcraft 3.3.5a (no install)\\'):
	filenames = {
		'crc': [f'Wow.crc', f'DivxDecoder.crc', f'unicows.crc'],
		'bin': ['Wow.exe', 'DivxDecoder.dll', 'unicows.dll']
	}

	crc_path = os.path.join(game_files_root, 'crc')
	bin_path = game_files_root
	if not os.path.exists(crc_path):
		os.mkdir(crc_path)

	buffer1 = bytearray(0x40)
	buffer2 = bytearray(0x40)

	for i in range(0, 0x40):
		buffer1[i] = 0x36
		buffer2[i] = 0x5c

	crc_salt = int_to_bytes(crc_salt)
	for i in range(0, len(crc_salt)):
		buffer1[i] ^= crc_salt[i]
		buffer2[i] ^= crc_salt[i]

	def make_crc_file(filename: str, checksum: bytes):
		path = os.path.join(crc_path, filename)
		with open(path, "wb") as f:
			f.write(checksum.hex().encode())

	#
	hash = sha1v(buffer1)
	for filename in filenames['crc']:
		path = os.path.join(crc_path, filename)

		if os.path.exists(path):
			with open(path, 'rb') as f:
				read_bytes = f.read()
				hash.update(bytes.fromhex(read_bytes.decode()))
		else:
			for bin in filenames['bin']:
				path = os.path.join(bin_path, bin)
				logger.debug(f'{path=}')

				if not os.path.exists(path):
					raise SrpChecksumNoGameFiles(f'File {path} not found')

				with open(path, 'rb') as f:
					file_bytes = f.read()
					hash.update(file_bytes)
					hash.update(bytes.fromhex(file_bytes.decode()))
					make_crc_file(os.path.join(crc_path, filename), sha1(file_bytes))
			break

	return bytes_to_int(sha1(client_public, sha1(buffer2, hash.digest())))