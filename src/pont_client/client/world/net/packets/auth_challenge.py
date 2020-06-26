import construct

from pont_client.client.world.net.packets.parse import parser
from pont_client.client.world.net.packets.constants import Opcode
from pont_client.client.world.net.packets.headers import ServerHeader

SMSG_AUTH_CHALLENGE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_CHALLENGE, 4 + 4 + 16*2),
	construct.Padding(4),
	'server_seed' / construct.ByteSwapped(construct.Int),
	'encryption_seed1' / construct.BytesInteger(16, swapped=True),
	'encryption_seed2' / construct.BytesInteger(16, swapped=True)
)

parser.set_parser(Opcode.SMSG_AUTH_CHALLENGE, SMSG_AUTH_CHALLENGE)