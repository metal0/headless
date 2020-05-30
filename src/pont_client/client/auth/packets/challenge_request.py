import time
import construct
from .constants import Response, Opcode, opcodes
from pont.utility.construct import UpperPascalString, IPv4Address

ChallengeRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_challenge, Opcode), opcodes.login_challenge),
	'response' / construct.Default(Response, Response.success),
	'packet_size' / construct.Short,
	'game' / construct.Default(construct.StringEncoded(construct.Byte[4], 'ascii'), 'WoW'),
	'version' / construct.Default(construct.Byte[3], [3, 3, 5]),
	'build' / construct.Default(construct.Short, 12340),
	'architecture' / construct.Default(construct.StringEncoded(construct.Byte[4], 'ascii'), 'x86'),
	'os' / construct.Default(construct.StringEncoded(construct.Byte[4], 'ascii'), 'Win'),
	'country' / construct.Default(construct.StringEncoded(construct.Byte[4], 'ascii'), 'enUS'),
	'timezone_bias' / construct.Default(construct.Int, int(-time.timezone / 60)),
	'ip' / construct.Default(IPv4Address, '127.0.0.1'),
	'account_name' / UpperPascalString('ascii'),
)
