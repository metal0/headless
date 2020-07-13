import construct

from ..opcode import Opcode
from .headers import ClientHeader, ServerHeader

CMSG_MESSAGECHAT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_MESSAGECHAT, 0),
)

SMSG_MESSAGECHAT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MESSAGECHAT, 0)
)

SMSG_GM_MESSAGECHAT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GM_MESSAGECHAT, 0)
)
