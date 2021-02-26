import construct

from ..opcode import Opcode
from .....utility.construct import PackEnum, int8
from pont.client.log import logger

def is_large_server_packet(data) -> bool:
	if type(data) is bytes:
		return (0x80 & int8(data[0])) == 0x80
	elif type(data) is int:
		return data > 0x7FFF
	else:
		return is_large_server_packet(data.size)

def ClientHeader(opcode = None, size = 0):
	if opcode is None:
		opcode_con = PackEnum(Opcode, construct.Int32ul)
	else:
		opcode_con = construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Int32ul)), opcode)

	return construct.Struct(
		'size' / construct.Default(construct.Int16ub, size + 4),
		'opcode' / opcode_con
	)

def _is_large_mask(context):
	return is_large_server_packet(bytes([context.mask]))

ServerSizeMask = construct.Struct(
	'mask' / construct.Byte,
	'rest' / construct.IfThenElse(
		_is_large_mask,
		construct.Bytes(2),
		construct.Bytes(1)
	)
)

class ServerSize(construct.Adapter):
	def __init__(self):
		super().__init__(ServerSizeMask)

	def _decode(self, obj, context, path) -> int:
		if is_large_server_packet(bytes([obj.mask])):
			return (int8(obj.mask << 16) & ~0x80) | (int8(obj.rest[0]) << 8) | int8(obj.rest[1])

		return (int8(obj.mask) << 8) | int8(obj.rest[0])

	def _encode(self, obj: int, context, path):
		if is_large_server_packet(obj):
			mask = (0x80 | int8(obj >> 16))
			rest = bytes([int8(obj >> 8), int8(obj)])

		else:
			mask = int8(obj >> 8)
			rest = bytes([int8(obj)])

		return dict(mask=mask, rest=rest)

def ServerHeader(opcode = None, size = 0):
	if opcode is None:
		opcode_con = construct.ByteSwapped(PackEnum(Opcode, construct.Short))
	else:
		opcode_con = construct.ByteSwapped(construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Short)), opcode))

	return construct.Struct(
		'size' / construct.Default(ServerSize(), size + 2),
		'opcode' / opcode_con
	)
