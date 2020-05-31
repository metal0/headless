import ipaddress
from typing import Tuple

import construct

from .string import int_to_bytes, bytes_to_int

def upper_filter(encoding):
	def _impl(char: bytes):
		if char.isascii():
			return char.decode().upper().encode(encoding)
		return char

	return _impl

UpperChar = lambda encoding: construct.Transformed(
	construct.Byte,
	decodefunc=upper_filter(encoding),
	decodeamount=1,
	encodefunc=upper_filter(encoding),
	encodeamount=1
)

class UpperPascalStringAdapter(construct.StringEncoded):
	def __init__(self, subcon, encoding):
		super().__init__(subcon, encoding)
		self.encoding = encoding
		self.filter = upper_filter(encoding)

	def _decode(self, obj, context, path):
		return obj.decode(self.encoding).upper()

	def _encode(self, obj, context, path):
		return bytes([len(obj)]) + obj.encode(self.encoding)

UpperPascalString = lambda encoding='ascii': UpperPascalStringAdapter(construct.GreedyBytes, encoding=encoding)

class PaddedStringByteSwappedAdapter(construct.Adapter):
	def __init__(self, length, encoding='ascii'):
		super().__init__(subcon=construct.GreedyBytes)
		self.length = length
		self.encoding = encoding

	def _encode(self, obj: str, context, path) -> bytes:
		print(f'_encode: {obj=}')
		bs = bytes(reversed(obj.encode(self.encoding)))
		result = bs + bytes([0] * (self.length - len(bs)))
		print(f'_encode: {result=}')
		return result

	def _decode(self, obj: bytes, context, path) -> str:
		subobj = obj[:self.length]
		print(f'_encode {self.name}: {obj=}, {subobj=}')
		subobj = bytes(reversed(subobj.replace(b'\x00', b'')))
		result = subobj.decode(self.encoding)
		print(f'_encode: {result=}')
		return result

PaddedStringByteSwapped = PaddedStringByteSwappedAdapter

class IPAddressAdapter(construct.Adapter):
	def _decode(self, obj, context, path):
		# TODO: Fix for v6
		ip = '.'.join(map(str, obj))
		return ipaddress.ip_address(ip)

	def _encode(self, obj, context, path):
		return ipaddress.ip_address(obj).packed

IPv4Address = IPAddressAdapter(construct.Byte[4])
# IPv6Address = IPAddressAdapter(construct.Byte[16])

class BigIntAdapter(construct.Adapter):
	def _decode(self, obj, context, path):
		return bytes_to_int(b''.join(bytes([b]) for b in obj))

	def _encode(self, obj, context, path):
		return int_to_bytes(obj)

BigInt = lambda size: BigIntAdapter(construct.Byte[size])

class ConstructEnumAdapter(construct.Enum):
	def __init__(self, enum_type, subcon, *merge, **mapping):
		super().__init__(subcon, *merge, **mapping)
		self.enum_type = enum_type

	def _decode(self, obj, context, path):
		print(f'_decode: {obj}')
		return self.enum_type(super()._decode(obj, context, path))

	def _encode(self, obj, context, path):
		print(f'_encode: {obj}')
		try:
			obj = obj.value
		except AttributeError:
			pass

		if isinstance(obj, Tuple):
			obj = obj[0]

		print(f'{type(self)}: {obj}')
		return super()._encode(int(obj), context, path)

ConstructEnum = lambda enum_type, subcon=construct.Byte: ConstructEnumAdapter(enum_type=enum_type, subcon=subcon)