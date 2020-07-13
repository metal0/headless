import construct

from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode

SMSG_BIND_POINT_UPDATE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_BIND_POINT_UPDATE, 8)
)