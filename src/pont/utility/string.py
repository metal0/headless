import binascii
import shlex


def int_to_bytes(value) -> bytes:
	if type(value) == bytes:
		return value

	hexed = '{:x}'.format(value)
	if len(hexed) % 2 == 1:
		hexed = "0" + hexed
	return binascii.unhexlify(hexed)[::-1]

def bytes_to_int(bytes) -> int:
	if type(bytes) == int:
		return bytes

	return int(binascii.hexlify(bytes[::-1]), 16)

def parse_address(address: str, default_port=3724):
	if ':' in address:
		return address.split(':')

	return address, default_port

def value_of_enum(enum):
	if isinstance(enum, int):
		return enum
	return enum.value

from typing import List
def parse_digits_list(l: List[int]) -> int:
	parity = 1
	num = 0
	for i, x in zip(reversed(range(0, len(l))), l):
		if x < 0:
			parity *= -1
		num += pow(10, i) * abs(x)

	return parity * num

def my_ip(p = None):
	return '0.0.0.0'
	# from urllib.request import urlopen
	# with urlopen('http://api.ipify.org') as response:
	# 	return response.read().decode()

from typing import Optional
def count_digits(num: Optional[int]) -> int:
	if num is None:
		return 0

	count = 0
	while num > 0:
		num = int(num / 10)
		count += 1

	return count

def dot_join(bs: bytes):
	return '.'.join(f'{c}' for c in bs)

def dot_split(s: str) -> bytes:
	ints = s.split('.')
	return bytes([int(i) for i in ints if i.isdigit()])

def decode_as_endian(data: bytes, endianness: str = '<'):
	if endianness != '<':
		return data.decode()
	else:
		return data.decode()[::-1].replace('\x00', '')

def string_encode(s: str, encoding = None) -> bytes:
	if isinstance(s, bytes):
		return s
	if encoding:
		return s.encode(encoding)
	return s.encode()

def latin_decode(s: bytes) -> str:
	return s.decode('latin1')

def reverse_encode(s: str) -> bytes:
	return s.encode()[::-1]

from typing import Iterator
def as_digits_list(num: Optional[int]) -> Iterator[int]:
	if not num:
		return []

	is_negative = (num < 0)
	if is_negative:
		num = abs(num)

	digits = [-(num % 10) if is_negative else (num % 10)]
	num = int(num / 10)
	while num > 0:
		digits.append(num % 10)
		num = int(num / 10)

	return reversed(digits)

def bin_to_hex(x: bytes) -> str:
	return hex(bytes_to_int(x))[2:]

def int_to_hex(x) -> hex:
	return hex(x).replace('0x', '')

