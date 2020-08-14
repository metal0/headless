from enum import Enum

import construct

from pont.utility.construct import PackEnum, UpperCString
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...expansion import Expansion

default_addon_bytes = b'\x9e\x02\x00\x00x\x9cu\xd2AN\xc30\x10\x05Pw\xc1\x19X\x94\x9b\xb0"\xa9\x14E\xd4\x9b\xc6\xac\xab\x89=$\xa3\xd8\xe3h\xe2\x94\xb6\xf7\xe0\x08\x9c\x8b\xab \x90@ \r\xeb\xaf7\xdf\x1e\xcd\xad1\xa6\x8at\xbd\x82\x84\xe3\x83\x1f\tO\x98\x90\xcbSk6\xe9\xe5no\xfe\xe4\x82\x0cz\xb2\xfaB\x99\xbf\xb3\xed\xfb\xcd\xdbOV\x81\xf4(\xcb\x98g\x95VPJ\xc4g\xc2\x18,1%\x98\xb5\x19\xc4\x81xP\x07\xd4\x10\x91\x03\x88\xc2\xea\x9cz(\xfb<h\xec+sx.\n\xdca\xbf\x0e.\xe7\xb8(\xb2\xb1\xf5\x08E\xfdkc\xbbUNxQ\x1f\xda\xc4\xcb<\xeal\xa5\x18*\xe0Iu-/3z\xbd\xb0-\x98\xba\xec\',\xff\xad\xc7\x82\x97\xac\xda\x03PP\x89\xfb\xdc\xa8\xde\xe7(\xa1\x05\x86\x01E\x83yB\xfd\x08\x9c@\xc0n\xa2\x18\xf5F\x01b\x94\xdf\xf4\xfeu\xf7\xf8\x01\\~\xda\x99'

CMSG_AUTH_SESSION = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUTH_SESSION, -4),
	'build' / construct.Default(construct.Int32ul, 12340),
	'login_server_id' / construct.Default(construct.Int32ul, 0),
	'account_name' / UpperCString('ascii'),
	'login_server_type' / construct.Default(construct.Int32ul, 0),
	'client_seed' / construct.Int32ul,
	'region_id' / construct.Default(construct.Int32ul, 0),
	'battlegroup_id' / construct.Default(construct.Int32ul, 0),
	'realm_id' / construct.Default(construct.Int32ul, 1),
	'dos_response' / construct.Default(construct.ByteSwapped(construct.Int64ul), 3),
	'account_hash' / construct.BytesInteger(20, swapped=True),
	'addon_info' / construct.Default(
		construct.GreedyBytes,
		# construct.Compressed(AddonsInfo, 'zlib'),
		default_addon_bytes
	),
)

SMSG_AUTH_CHALLENGE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_CHALLENGE, 40),
	construct.Padding(4),
	'server_seed' / construct.Int32ul,
	'encryption_seed1' / construct.BytesInteger(16, swapped=True),
	'encryption_seed2' / construct.BytesInteger(16, swapped=True)
)

class AuthResponse(Enum):
	ok = 0x0C
	failed = 0x0D
	reject = 0x0E
	bad_server_proof = 0x0F
	unavailable = 0x10
	system_error = 0x11
	billing_error = 0x12
	billing_expired = 0x13
	version_mismatch = 0x14
	unknown_account = 0x15
	incorrect_password = 0x16
	session_expired = 0x17
	server_shutting_down = 0x18
	already_logging_in = 0x19
	login_server_not_found = 0x1A
	wait_queue = 0x1B
	banned = 0x1C
	already_online = 0x1D
	no_time = 0x1E
	db_busy = 0x1F
	suspended = 0x20
	parental_control = 0x21

SMSG_AUTH_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_RESPONSE, 15),
	'response' / PackEnum(AuthResponse),
	'billing_time_remaining' / construct.ByteSwapped(construct.Default(construct.Int, 0)),
	'billing_plan_flags' / construct.Default(construct.Byte, 0),
	'billing_time_rested' / construct.ByteSwapped(construct.Default(construct.Int, 0)),
	'expansion' / construct.Default(PackEnum(Expansion), Expansion.wotlk),
	'queue_position' / construct.Default(construct.Switch(
		construct.this.response == AuthResponse.wait_queue, {
			True: construct.Int32ul,
			False: construct.Pass
		}
	), construct.Pass)
)
