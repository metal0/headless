import construct

from pont.utility.construct import PackEnum
from ..opcode import Opcode

ProofRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_proof, PackEnum(Opcode)), Opcode.login_proof),
	'client_public' / construct.BytesInteger(32, swapped=True),
	'session_proof' / construct.BytesInteger(20, swapped=True),
	'checksum' / construct.BytesInteger(20, swapped=True),
	'num_keys' / construct.Default(construct.Byte, 0),
	'security_flags' / construct.Default(construct.Byte, 0),
)