import time
import construct
from .constants import Response, Opcode, opcodes
from ....utility.construct import UpperPascalString, IPv4Address, ConstructEnum, PaddedStringByteSwapped

ChallengeRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_challenge, ConstructEnum(Opcode)), opcodes.login_challenge),
	'response' / construct.Default(ConstructEnum(Response), Response.db_busy),
	'packet_size' / construct.ByteSwapped(construct.Short),
	'game' / construct.Default(construct.PaddedString(4, 'ascii'), 'WoW'),
	'version' / construct.Default(construct.Array(3, construct.Byte), [3, 3, 5]),
	'build' / construct.Default(construct.ByteSwapped(construct.Short), 12340),
	'architecture' / construct.Default(PaddedStringByteSwapped(4), 'x86'),
	'os' / construct.Default(PaddedStringByteSwapped(4), 'Win'),
	'country' / construct.Default(PaddedStringByteSwapped(4), 'enUS'),
	'timezone_bias' / construct.Default(construct.ByteSwapped(construct.Int32sb), int(-time.timezone / 60)),
	'ip' / construct.Default(construct.ByteSwapped(IPv4Address), '127.0.0.1'),
	'account_name' / UpperPascalString('ascii'),
)
