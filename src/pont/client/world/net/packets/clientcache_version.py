import construct

from .headers import ServerHeader
from ..opcode import Opcode

SMSG_CLIENTCACHE_VERSION = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CLIENTCACHE_VERSION, 4),
	'version' / construct.Default(construct.Int32ul, 3),
)
