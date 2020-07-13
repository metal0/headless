import os
from typing import Tuple

import srptools

from pont.client.auth.errors import InvalidLogin
from pont.client.log import mgr
from pont.utility.string import int_to_bytes, bytes_to_int
from .sha import sha1, sha1v

log = mgr.get_logger(__name__)

class WowSrpClient(object):
	def __init__(self, username: str, password: str, prime: int, generator: int, client_private = None):
		multiplier = 3
		self.__username = username.upper()
		self.__password = password.upper()
		self.__srptools = srptools.SRPContext(
			self.__username, self.__password,
			prime = hex(prime), generator = hex(generator),
			multiplier = hex(multiplier)
		)

		self.prime = prime
		self.generator = generator
		if not client_private:
			self.client_private = self.__srptools.generate_client_private()
		else:
			self.client_private = client_private

		log.debug(f'{self.client_private=}')
		self.client_public = self.__srptools.get_client_public(self.client_private)
		if self.client_public == 0:
			raise InvalidLogin('client_public must not be zero')

		self.password_hash = 0
		self.password_verifier = 0
		self.common_secret = 0
		self.client_premaster_secret = 0
		self.session_key = 0
		self.session_proof = 0
		self.session_proof_hash = 0

	def process(self, server_public: int, salt: int) -> Tuple[int, int]:
		"""Returns: client_public, session_proof"""
		prehash = sha1(f'{self.__username}:{self.__password}')
		self.password_hash = sha1(salt, prehash, out=int)
		self.password_verifier = self.__srptools.get_common_password_verifier(password_hash=self.password_hash)

		self.common_secret = sha1(self.client_public, server_public, out=int)

		# this is S
		self.client_premaster_secret = self.__srptools.get_client_premaster_secret(
			server_public=server_public,
			client_private=self.client_private,
			password_hash=self.password_hash,
			common_secret=self.common_secret
		)


		# this is K
		self.session_key = self.sha_interleave(self.client_premaster_secret)
		self.session_proof, self.session_proof_hash = self.compute_proof(salt=salt, server_public=server_public)
		self.__username = None
		self.__password = None
		return bytes_to_int(self.client_public), self.session_proof

	@staticmethod
	def sha_interleave(value: int) -> bytes:
		t = int_to_bytes(value)

		t1 = list()
		for i in range(0, 32, 2):
			t1.append(t[i])

		sha = sha1(t1)
		result = list(range(0, 40))

		# fill even result entries [0], [2] etc.
		for i in range(0, 20):
			result[i * 2] = sha[i]

		for i in range(0, 16):
			t1[i] = t[i * 2 + 1]

		sha = sha1(t1)
		# fill uneven result entries [1], [3] etc.
		for i in range(0, 20):
			result[i * 2 + 1] = sha[i]

		return bytes(result)

	def compute_proof(self, salt: int, server_public: int) -> Tuple[int, int]:
		N_sha = sha1(self.prime, out=int)
		g_sha = sha1(self.generator, out=int)

		# calculated M1
		session_proof = sha1(
			N_sha ^ g_sha,
			sha1(self.__username),
			salt,
			self.client_public,
			server_public,
			self.session_key
		)

		hash = sha1(self.client_public, session_proof, self.session_key)
		return bytes_to_int(session_proof), bytes_to_int(hash)

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
				log.debug(f'{path=}')

				if not os.path.exists(path):
					raise SrpChecksumNoGameFiles(f'File {path} not found')

				with open(path, 'rb') as f:
					file_bytes = f.read()
					hash.update(file_bytes)
					hash.update(bytes.fromhex(file_bytes.decode()))
					make_crc_file(os.path.join(crc_path, filename), sha1(file_bytes))
			break

	return bytes_to_int(sha1(client_public, sha1(buffer2, hash.digest())))