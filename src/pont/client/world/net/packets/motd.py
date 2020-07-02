import construct

from pont.client.world.net.packets.parse import parser
from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_MOTD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MOTD, 4),
	'lines' / construct.PrefixedArray(construct.Int, construct.CString('ascii'))
)

parser.set_parser(Opcode.SMSG_MOTD, SMSG_MOTD)