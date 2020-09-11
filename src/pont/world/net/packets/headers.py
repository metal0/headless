import construct

from ..opcode import Opcode


def ClientHeader(opcode = None, size = 0):
	from .....utility.construct import PackEnum
	if opcode is None:
		opcode_con = construct.ByteSwapped(PackEnum(Opcode, construct.Int))
	else:
		opcode_con = construct.ByteSwapped(construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Int)), opcode))

	return construct.Struct(
		'size' / construct.Default(construct.Short, size + 4),
		'opcode' / opcode_con
	)

def ServerHeader(opcode = None, size = 0):
	from .....utility.construct import PackEnum
	if opcode is None:
		opcode_con = construct.ByteSwapped(PackEnum(Opcode, construct.Short))
	else:
		opcode_con = construct.ByteSwapped(construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Short)), opcode))

	return construct.Struct(
		'size' / construct.Default(construct.Short, size + 2),
		'opcode' / opcode_con
	)

def is_large_packet(data: bytes) -> bool:
	return (0x80 & data[0]) == 0x80