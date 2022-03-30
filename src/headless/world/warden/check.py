import hashlib
import construct
from typing import Union
from enum import Enum

from wlink.utility.construct import int32

from .sha1_randx import SHA1Randx


class CheatCheckType(Enum):
	memory_check = 0xF3        # 243: byte moduleNameIndex + uint Offset + byte Len (check to ensure memory isn't modified)
	page_check_a = 0xB2        # 178: uint Seed + byte[20] SHA1 + uint Addr + byte Len (scans all pages for specified hash)
	page_check_b = 0xBF        # 191: uint Seed + byte[20] SHA1 + uint Addr + byte Len (scans only pages starts with MZ+PE headers for specified hash)
	mpq_check = 0x98           # 152: byte fileNameIndex (check to ensure MPQ file isn't modified)
	lua_string_check = 0x8B    # 139: byte luaNameIndex (check to ensure LUA string isn't used)
	driver_check = 0x71        # 113: uint Seed + byte[20] SHA1 + byte driverNameIndex (check to ensure driver isn't loaded)
	timing_check = 0x57        #  87: empty (check to ensure GetTickCount() isn't detoured)
	process_check = 0x7E       # 126: uint Seed + byte[20] SHA1 + byte moluleNameIndex + byte procNameIndex + uint Offset + byte Len (check to ensure proc isn't detoured)
	unknown_check = 217

CheatChecksRequest = construct.Struct(
	'name' / construct.PascalString(construct.Byte, 'ascii'),
	'data' / construct.GreedyBytes,
)

class WardenCheckManager:
	def __init__(self):
		pass


def signed_xor(x, y, len, byteorder='little', x_signed=True, y_signed=True):
	x_bs = int.to_bytes(x, len, byteorder, signed=x_signed)
	y_bs = int.to_bytes(y, len, byteorder, signed=y_signed)

	res = bytes([a ^ b for (a, b) in zip(x_bs, y_bs)])
	return int.from_bytes(res, byteorder, signed=True)
#
#
# def calculate_hash_result(seed: Union[bytes, int], id: Union[str, bytes]):
# 	if type(id) is bytes:
# 		id = id.hex()
#
# 	if type(seed) is int:
# 		seed = int.to_bytes(seed, 16, 'little')
#
# 	# TODO: Fix this
# 	if seed == b'M\x80\x8d,w\xd9\x05\xc4\x1ac\x80\xec\x08Xj\xfe' and id == '79c0768d657977d697e10bad956cced1':
# 		known_client_key = bytes([0x7F, 0x96, 0xEE, 0xFD, 0xA5, 0xB6, 0x3D, 0x20, 0xA4, 0xDF, 0x8E, 0x00, 0xCB, 0xF4, 0x83, 0x04])
# 		known_server_key = bytes([0xC2, 0xB7, 0xAD, 0xED, 0xFC, 0xCC, 0xA9, 0xC2, 0xBF, 0xB3, 0xF8, 0x56, 0x02, 0xBA, 0x80, 0x9B])
# 		return hashlib.sha1(known_client_key).digest(), known_client_key, known_server_key
#
# 	client_key = [
# 		int.from_bytes(seed[i:i + 4], 'little', signed=True) for i in range(0, 16, 4)
# 	]
#
# 	server_key = [0] * 4
# 	server_key[0] = client_key[0]
# 	client_key[0] = signed_xor(client_key[0], 0xDEADBEEF, 4, y_signed=False)
#
# 	server_key1 = client_key[1]
# 	client_key[1] = int32(client_key[1] - 0x35014542)
# 	server_key2 = client_key[2]
#
# 	client_key[2] = int32(client_key[2] + 0x5313F22)
# 	client_key[3] = int32(client_key[3] * 0x1337F00D)
#
# 	server_key[1] = int32(server_key1 - 0x6A028A84)
# 	server_key[2] = int32(server_key2 + 0xA627E44)
# 	server_key[3] = int32(client_key[3] * 0x1337F00D)
# 	print(client_key)
# 	print(server_key)
#
# 	client_key_bytes = bytearray()
# 	for i in client_key:
# 		data = int.to_bytes(i, 4, 'little', signed=True)
# 		client_key_bytes.extend(data)
#
# 	server_key_bytes = bytearray()
# 	for i in server_key:
# 		data = int.to_bytes(i, 4, 'little', signed=False)
# 		server_key_bytes.extend(data)
#
# 	print(client_key_bytes.hex())
# 	print(server_key_bytes.hex())
# 	# raise WorldError('Warden danger!')
# 	return hashlib.sha1(client_key_bytes).digest(), bytes(client_key_bytes), bytes(server_key_bytes)