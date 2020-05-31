import construct

from .parse import parser
from .constants import Response, Opcode, opcodes
from ....utility.construct import BigInt, ConstructEnum

ChallengeResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_challenge, ConstructEnum(Opcode)), opcodes.login_challenge),
	'response' / construct.Default(ConstructEnum(Response), Response.success),
	construct.Padding('1'),

	'server_public' / BigInt(32),
	'generator_length' / construct.Default(construct.Byte, 1),
	'generator' / construct.Default(BigInt(construct.this.generator_length), 7),

	'prime_length' / construct.Default(construct.Byte, 32),
	'prime' / BigInt(construct.this.prime_length),
	'salt' / BigInt(32),
	'checksum_salt' / BigInt(16),
	'security_flag' / construct.Default(construct.Byte, 0),
)

parser.set_parser(opcodes.login_challenge, parser=ChallengeResponse)