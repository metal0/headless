import ipaddress
import construct

from pont.utility.string import int_to_bytes, bytes_to_int


def upper_filter(encoding):
	def _impl(char: bytes) -> bytes:
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

UpperPascalString = lambda encoding: construct.StringEncoded(construct.Prefixed(construct.Byte, construct.GreedyRange(UpperChar(encoding))), encoding)

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
		return self.enum_type(super()._decode(obj, context, path))

	def _encode(self, obj, context, path):
		try:
			obj = obj.value
		except AttributeError:
			pass

		return super()._encode(int(obj), context, path)

ConstructEnum = lambda enum_type, subcon=construct.Byte: ConstructEnumAdapter(enum_type=enum_type, subcon=subcon)