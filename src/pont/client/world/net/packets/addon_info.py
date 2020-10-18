import construct

from .headers import ServerHeader
from ..opcode import Opcode

# TODO: There is DOS potential here as well as with SMSG_ADDON_INFO as mentioned on the TrinityCore Github.
#  I suspect this is due to world protocol using zlib DEFLATE compression, which is susceptible to decompression bombs.
#  Though I don't know how effective this will be in the context of TCP streams.
SMSG_ADDON_INFO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_ADDON_INFO, 4),
	'unk' / construct.GreedyBytes,
)