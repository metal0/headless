import ipaddress
import construct
from typing import Tuple, Union, NamedTuple

class GuidConstruct(construct.Adapter):
	def __init__(self, guid_type):
		super().__init__(construct.Int64ul)
		self.guid_type = guid_type

	def _decode(self, obj: int, context, path):
		return self.guid_type(value=obj)

	def _encode(self, obj, context, path) -> int:
		return obj.value

def FixedString(length, encoding='ascii'):
	return construct.StringEncoded(construct.FixedSized(length, construct.GreedyBytes), encoding)

class UpperCString(construct.Adapter):
	def __init__(self, encoding='ascii'):
		super().__init__(construct.CString(encoding))
		self.encoding = encoding

	def _decode(self, obj: str, context, path) -> str:
		return obj.upper()

	def _encode(self, obj: str, context, path) -> str:
		return obj.upper()

class UpperPascalStringAdapter(construct.StringEncoded):
	def __init__(self, subcon, encoding):
		super().__init__(subcon, encoding)

	def _decode(self, obj, context, path):
		length = obj[0]
		return obj[1:length + 1].decode(self.encoding).upper()

	def _encode(self, obj, context, path):
		obj = obj.upper()
		return bytes([len(obj)]) + obj.encode(self.encoding)

UpperPascalString = lambda encoding='ascii': UpperPascalStringAdapter(construct.GreedyBytes, encoding=encoding)

class PaddedStringByteSwappedAdapter(construct.StringEncoded):
	def __init__(self, length, encoding='ascii'):
		super().__init__(construct.Bytes(length), encoding=encoding)
		self.length = length

	def _encode(self, obj: str, context, path) -> bytes:
		bs = bytes(reversed(obj.encode(self.encoding)))
		result = bs + bytes([0] * (self.length - len(bs)))
		return result

	def _decode(self, obj: bytes, context, path) -> str:
		subobj = obj[:self.length]
		subobj = bytes(reversed(subobj.replace(b'\x00', b'')))
		result = subobj.decode(self.encoding)
		return result

PaddedStringByteSwapped = PaddedStringByteSwappedAdapter

class AddressPort(construct.Adapter):
	def __init__(self, encoding='ascii', separator=':'):
		super().__init__(construct.CString(encoding))
		self.separator = separator
		self.encoding = encoding

	def _encode(self, obj: Union[Tuple[str, int], str], context, path) -> str:
		if type(obj) == str:
			ip, port = obj.split(self.separator)
		else:
			ip, port = obj

		addr_string = f'{ip}{self.separator}{port}'
		return addr_string

	def _decode(self, obj: str, context, path) -> Tuple[str, int]:
		ip, port = obj.split(self.separator)
		return ip, int(port)

class IPAddressAdapter(construct.Adapter):
	def _decode(self, obj, context, path):
		# TODO: Fix for v6
		ip = '.'.join(map(str, obj))
		return str(ipaddress.ip_address(ip))

	def _encode(self, obj, context, path):
		return ipaddress.ip_address(obj).packed

IPv4Address = IPAddressAdapter(construct.Bytes(4))
# IPv6Address = IPAddressAdapter(construct.Byte[16])

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

		if isinstance(obj, Tuple):
			obj = obj[0]

		return super()._encode(int(obj), context, path)

PackEnum = lambda enum_type, subcon=construct.Byte: ConstructEnumAdapter(enum_type=enum_type, subcon=subcon)

class VersionStringFromBytesAdapter(construct.StringEncoded):
	def __init__(self, num_bytes, encoding='ascii'):
		super().__init__(construct.Bytes(length=num_bytes), encoding)

	def _decode(self, obj: bytes, context, path):
		return '.'.join([str(b) for b in obj])

	def _encode(self, obj: str, context, path):
		return bytes(list(map(int, obj.split('.'))))

VersionString = VersionStringFromBytesAdapter

Coordinates = lambda float_con = construct.Float32b: construct.Struct(
	'x' / float_con,
	'y' / float_con,
	'z' / float_con,
)

class PackedCoordinates(construct.Adapter):
	def __init__(self, position_type):
		super().__init__(construct.Int)
		self.position_type = position_type

	def _decode(self, obj: int, context, path) -> NamedTuple:
		x = ((obj & 0x7FF) << 21 >> 21) * 0.25
		y = ((((obj >> 11) & 0x7FF) << 21) >> 21) * 0.25
		z = ((obj >> 22 << 22) >> 22) * 0.25
		return self.position_type(x, y, z)

	def _encode(self, obj, context, path) -> int:
		value = 0
		value |= (int(obj.x / 0.25) & 0x7FF)
		value |= (int(obj.y / 0.25) & 0x7FF) << 11
		value |= (int(obj.z / 0.25) & 0x3FF) << 22
		return value

def _compute_packed_guid_byte_size(mask) -> int:
	return sum(1 for i in range(8) if mask & (1 << i))

def compute_mask_size(context) -> int:
	return _compute_packed_guid_byte_size(context.mask)

def pack_guid(guid: int):
	mask = 0
	result = bytearray()

	print(f'pack_guid: {guid=}')
	print(f'{guid >> 7 * 8}')

	for i in range(8):
		if guid == 0:
			break

		if guid & 0xFF:
			print(f'pack_guid: {guid=}, {i=}, {bin(mask)=}, {result=}')
			mask |= (1 << i)
			result.append(guid & 0xFF)

		guid >>= 8

	# result.append((guid >> 7 * 8) & )

	return mask, bytes(result)

def unpack_guid(mask: int, data: bytes) -> int:
	guid = 0
	data = bytearray(data)

	for i in range(8):
		if mask & (1 << i):
			guid |= (data.pop(0) << (i * 8))

	return guid

class GuidUnpacker(construct.Adapter):
	def __init__(self, guid_type):
		super().__init__(construct.Struct(
			"mask" / construct.Byte,
			"data" / construct.Bytes(compute_mask_size)
		))

		self.guid_type = guid_type

	def _decode(self, obj, context, path):
		print(f'_decode: {context=}')
		print(obj)

		return self.guid_type(value=unpack_guid(obj.mask, obj.data))

	def _encode(self, obj, context, path):
		print(f'_encode: {context=}')
		print(obj)

		mask, data = pack_guid(obj.value)
		return {"mask": mask, "data": data}

def int8(num: int):
	return 0xFF & num