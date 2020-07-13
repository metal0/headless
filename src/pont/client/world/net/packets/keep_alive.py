import construct

from ..opcode import Opcode
from .headers import ClientHeader

CMSG_KEEP_ALIVE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_KEEP_ALIVE, 0)
)