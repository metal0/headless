import time
import construct
from .constants import Response, Opcode
from pont_client.utility.construct import UpperPascalString, IPv4Address, ConstructEnum, PaddedStringByteSwapped, \
	VersionString

ChallengeRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_challenge, ConstructEnum(Opcode)), Opcode.login_challenge),
	'response' / construct.Default(ConstructEnum(Response), Response.db_busy),
	'packet_size' / construct.ByteSwapped(construct.Default(construct.Short, 34 + construct.len_(construct.this.account_name))),
	'game' / construct.Default(construct.PaddedString(4, 'ascii'), 'WoW'),
	'version' / construct.Default(VersionString(num_bytes=3), '3.3.5'),
	'build' / construct.Default(construct.ByteSwapped(construct.Short), 12340),
	'architecture' / construct.Default(PaddedStringByteSwapped(4), 'x86'),
	'os' / construct.Default(PaddedStringByteSwapped(4), 'Win'),
	'country' / construct.Default(PaddedStringByteSwapped(4), 'enUS'),
	'timezone_bias' / construct.Default(construct.ByteSwapped(construct.Int32sb), int(-time.timezone / 60)),
	'ip' / construct.Default(IPv4Address, '127.0.0.1'),
	'account_name' / UpperPascalString('ascii'),
)
