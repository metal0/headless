import construct

from pont.client.world.net.packets.parse import parser
from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ServerHeader

SMSG_ADDON_INFO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_ADDON_INFO, 4),
	'unk' / construct.GreedyBytes,
)

parser.set_parser(Opcode.SMSG_ADDON_INFO, SMSG_ADDON_INFO)