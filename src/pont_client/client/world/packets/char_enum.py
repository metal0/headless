from pont.client.world.opcode import Opcode, opcodes
from pont.utility.string import value_of_enum
from pont.utility.packed_struct import StructField, PackAs, pack_struct

@pack_struct
class SMSG_CHAR_ENUM:
	opcode = StructField(PackAs.byte(), default=lambda p: opcodes.SMSG_CHAR_ENUM, decode=Opcode, encode=value_of_enum)


