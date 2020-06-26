import construct

from pont_client.client.world.net.packets import parser
from pont_client.client.world.net.packets.constants import Opcode
from pont_client.utility.construct import PackEnum

SMSG_PONG = construct.Struct(
	'opcode' / construct.Default(construct.Const(
		Opcode.SMSG_PONG,
		PackEnum(Opcode, construct.ByteSwapped(construct.Int))),
		Opcode.SMSG_PONG
	),
)

parser.set_parser(Opcode.SMSG_PONG, SMSG_PONG)