import construct

from .header import ResponseHeader
from ..opcode import Opcode

ChallengeResponse = construct.Struct(
	'header' / ResponseHeader(Opcode.login_challenge),
	construct.Padding(1),

	'server_public' / construct.BytesInteger(32, swapped=True),
	'generator_length' / construct.Default(construct.Byte, 1),
	'generator' / construct.Default(construct.BytesInteger(construct.this.generator_length, swapped=True), 7),

	'prime_length' / construct.Default(construct.Byte, 32),
	'prime' / construct.BytesInteger(construct.this.prime_length, swapped=True),
	'salt' / construct.BytesInteger(32, swapped=True),
	'checksum' / construct.BytesInteger(16, swapped=True),
	'security_flag' / construct.Default(construct.Byte, 0),
)
