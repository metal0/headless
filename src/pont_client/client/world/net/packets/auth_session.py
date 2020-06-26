import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.client.world.net.packets.headers import ClientHeader
from pont_client.utility.construct import UpperCString

# Fixes the header size of the packet once all of the fields have been parsed
# If the user explicitly chose a header size (other than 0) then their choice will have precedence.
def _adjust_header_size(ctx):
	print('[_adjust_header_size]')
	print(ctx.header)
	if ctx.header.size == 0:
		construct.this.header.size = 61 + len(ctx.addon_info) + len(ctx.account_name)
		ctx.header.size = 61 + len(ctx.addon_info) + len(ctx.account_name)
	return None

CMSG_AUTH_SESSION = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUTH_SESSION, -4),
	'build' / construct.Default(construct.ByteSwapped(construct.Int), 12340),
	'login_server_id' / construct.Default(construct.ByteSwapped(construct.Int), 0),
	'account_name' / UpperCString('ascii'),
	'login_server_type' / construct.Default(construct.ByteSwapped(construct.Int), 0),
	'client_seed' / construct.ByteSwapped(construct.Int),
	'region_id' / construct.Default(construct.ByteSwapped(construct.Int), 0),
	'battlegroup_id' / construct.Default(construct.ByteSwapped(construct.Int), 0),
	'realm_id' / construct.Default(construct.ByteSwapped(construct.Int), 1),
	'dos_response' / construct.Default(construct.ByteSwapped(construct.Int64ul), 3),
	'account_hash' / construct.BytesInteger(20, swapped=True),
	'addon_info' / construct.Default(
		construct.GreedyBytes,
		b'\x9e\x02\x00\x00x\x9cu\xd2AN\xc30\x10\x05Pw\xc1\x19X\x94\x9b\xb0"\xa9\x14E\xd4\x9b\xc6\xac\xab\x89=$\xa3\xd8\xe3h\xe2\x94\xb6\xf7\xe0\x08\x9c\x8b\xab \x90@ \r\xeb\xaf7\xdf\x1e\xcd\xad1\xa6\x8at\xbd\x82\x84\xe3\x83\x1f\tO\x98\x90\xcbSk6\xe9\xe5no\xfe\xe4\x82\x0cz\xb2\xfaB\x99\xbf\xb3\xed\xfb\xcd\xdbOV\x81\xf4(\xcb\x98g\x95VPJ\xc4g\xc2\x18,1%\x98\xb5\x19\xc4\x81xP\x07\xd4\x10\x91\x03\x88\xc2\xea\x9cz(\xfb<h\xec+sx.\n\xdca\xbf\x0e.\xe7\xb8(\xb2\xb1\xf5\x08E\xfdkc\xbbUNxQ\x1f\xda\xc4\xcb<\xeal\xa5\x18*\xe0Iu-/3z\xbd\xb0-\x98\xba\xec\',\xff\xad\xc7\x82\x97\xac\xda\x03PP\x89\xfb\xdc\xa8\xde\xe7(\xa1\x05\x86\x01E\x83yB\xfd\x08\x9c@\xc0n\xa2\x18\xf5F\x01b\x94\xdf\xf4\xfeu\xf7\xf8\x01\\~\xda\x99'
	),
	# construct.Computed(_adjust_header_size),
)

