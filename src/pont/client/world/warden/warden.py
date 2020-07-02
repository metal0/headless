import construct
from enum import Enum

class ServerCommand(Enum):
	module_use = 0
	module_cache = 1
	cheat_checks_request = 2
	module_initialize = 3
	memory_check_request = 4
	hash_request = 5

class ClientCommand(Enum):
	module_missing = 0
	module_ok = 1
	cheat_check_result = 2
	memory_check_result = 3
	hash_result = 4
	module_failed = 5

ServerModuleInfoRequest = construct.Struct(
	'id' / construct.BytesInteger(length=16, swapped=True),
	'key' / construct.BytesInteger(length=16, swapped=True),
	'size' / construct.ByteSwapped(construct.Int)
)

ServerModuleTransferRequest = construct.Struct(
	'data' / construct.FixedSized(500, construct.PrefixedArray(construct.ByteSwapped(construct.Short), construct.Byte))
)

InitModuleRequest = construct.Struct(
	'command1' / construct.Byte,
	'size1' / construct.ByteSwapped(construct.Short),
	'checksum1' / construct.ByteSwapped(construct.Int),
	'unk1' / construct.Bytes(2),
	'type' / construct.Byte,
	'string_library1' / construct.Byte,
	'function1' / construct.Array(4, construct.ByteSwapped(construct.Int)),

	'command2' / construct.Byte,
	'size2' / construct.ByteSwapped(construct.Short),
	'checksum2' / construct.ByteSwapped(construct.Int),
	'unk2' / construct.Bytes(2),
	'string_library2' / construct.Byte,
	'function2' / construct.ByteSwapped(construct.Int),
	'function2_set' / construct.Byte,

	'command3' / construct.Byte,
	'size3' / construct.ByteSwapped(construct.Short),
	'checksum3' / construct.ByteSwapped(construct.Int),
	'unk3' / construct.Bytes(2),
	'string_library3' / construct.Byte,
	'function3' / construct.ByteSwapped(construct.Int),
	'function3_set' / construct.Byte,
)

ServerHashRequest = construct.Struct(
	'seed' / construct.BytesInteger(length=16, swapped=True)
)

ClientModule = construct.Struct(
	'id' / construct.BytesInteger(length=16, swapped=True),
	'key' / construct.BytesInteger(length=16, swapped=True),
	'data' / construct.PrefixedArray(construct.ByteSwapped(construct.Int), construct.Byte)
)

class Warden:
	pass

