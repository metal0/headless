import construct

from .parse import parser
from .constants import Response, Opcode
from pont_client.utility.construct import ConstructEnum

ChallengeResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_challenge, ConstructEnum(Opcode)), Opcode.login_challenge),
	'response' / construct.Default(ConstructEnum(Response), Response.success),
	construct.Padding(1),

	'server_public' / construct.BytesInteger(32, swapped=True),
	'generator_length' / construct.Default(construct.Byte, 1),
	'generator' / construct.Default(construct.BytesInteger(construct.this.generator_length, swapped=True), 7),

	'prime_length' / construct.Default(construct.Byte, 32),
	'prime' / construct.BytesInteger(construct.this.prime_length, swapped=True),
	'salt' / construct.BytesInteger(32, swapped=True),
	'checksum_salt' / construct.BytesInteger(16, swapped=True),
	'security_flag' / construct.Default(construct.Byte, 0),
)

parser.set_parser(Opcode.login_challenge, parser=ChallengeResponse)