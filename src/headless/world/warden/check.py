import construct
from enum import Enum


class CheatCheckType(Enum):
	memory_check = 0xF3        # 243: byte moduleNameIndex + uint Offset + byte Len (check to ensure memory isn't modified)
	page_check_a = 0xB2        # 178: uint Seed + byte[20] SHA1 + uint Addr + byte Len (scans all pages for specified hash)
	page_check_b = 0xBF        # 191: uint Seed + byte[20] SHA1 + uint Addr + byte Len (scans only pages starts with MZ+PE headers for specified hash)
	mpq_check = 0x98           # 152: byte fileNameIndex (check to ensure MPQ file isn't modified)
	lua_string_check = 0x8B    # 139: byte luaNameIndex (check to ensure LUA string isn't used)
	driver_check = 0x71        # 113: uint Seed + byte[20] SHA1 + byte driverNameIndex (check to ensure driver isn't loaded)
	timing_check = 0x57        #  87: empty (check to ensure GetTickCount() isn't detoured)
	process_check = 0x7E       # 126: uint Seed + byte[20] SHA1 + byte moluleNameIndex + byte procNameIndex + uint Offset + byte Len (check to ensure proc isn't detoured)

CheatChecksRequest = construct.Struct(
	'name' / construct.PascalString(construct.Byte, 'ascii'),
	'oof' / construct.GreedyBytes,
)