import construct

from pont_client.utility.construct import ConstructEnum
from .constants import Opcode

ProofRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_proof, ConstructEnum(Opcode)), Opcode.login_proof),
	'client_public' / construct.BytesInteger(32, swapped=True),
	'session_proof' / construct.BytesInteger(20, swapped=True),
	'checksum' / construct.BytesInteger(20, swapped=True),
	'num_keys' / construct.Default(construct.Byte, 0),
	'security_flags' / construct.Default(construct.Byte, 0),
)