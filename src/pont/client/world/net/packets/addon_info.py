import construct

from .headers import ServerHeader
from ..opcode import Opcode

# TODO: Research zip bomb idea here for potential worldserver DOS exploit

SMSG_ADDON_INFO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_ADDON_INFO, 4),
	'unk' / construct.GreedyBytes,
)