import construct

from .constants import Opcode
from .headers import ServerHeader
from .parse import parser

# TODO: Research zip bomb idea here for potential worldserver DOS exploit
SMSG_ADDON_INFO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_ADDON_INFO, 4),
	'unk' / construct.GreedyBytes,
)

parser.set_parser(Opcode.SMSG_ADDON_INFO, SMSG_ADDON_INFO)