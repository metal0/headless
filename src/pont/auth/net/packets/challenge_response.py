import construct

from pont.utility.construct import PackEnum
from ..opcode import Opcode
from ..response import Response

ChallengeResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_challenge, PackEnum(Opcode)), Opcode.login_challenge),
	'response' / construct.Default(PackEnum(Response), Response.success),
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
