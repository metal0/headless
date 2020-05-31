import construct

from pont_client.utility.construct import ConstructEnum, BigInt
from .constants import Opcode, opcodes

ProofRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_proof, ConstructEnum(Opcode)), opcodes.login_proof),
	'client_public' / BigInt(32),
	'session_proof' / BigInt(20),
	'checksum' / BigInt(20),
	'num_keys' / construct.Default(construct.Byte, 0),
	'security_flags' / construct.Default(construct.Byte, 0),
)