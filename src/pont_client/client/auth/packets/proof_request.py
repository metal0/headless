import construct
from .constants import Opcode, opcodes
from pont.utility.construct import BigInt

ProofRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_proof, Opcode), opcodes.login_proof),
	'client_public' / BigInt(32),
	'session_proof' / BigInt(20),
	'checksum' / BigInt(20),
	'num_keys' / construct.Default(construct.Byte, 0),
	'security_flags' / construct.Default(construct.Byte, 0),
)