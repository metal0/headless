import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.utility.construct import PackEnum

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'size' / construct.Default(construct.Short, 4*4+2),
	'opcode' / construct.Const(
		Opcode.SMSG_AUTH_CHALLENGE,
		construct.Default(
			construct.ByteSwapped(PackEnum(Opcode, construct.Short)),
			Opcode.SMSG_AUTH_CHALLENGE
		)
	),
	'map' / construct.Int,
	'x' / construct.Float32b,
	'y' / construct.Float32b,
	'z' / construct.Float32b,
	'rotation' / construct.Float32b,
)