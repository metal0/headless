import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.utility.construct import PackEnum

SMSG_AUTH_CHALLENGE = construct.Struct(
	'size' / construct.Short,
	'opcode' / construct.Const(
		Opcode.SMSG_AUTH_CHALLENGE,
		construct.Default(
			construct.ByteSwapped(PackEnum(Opcode, construct.Short)),
			Opcode.SMSG_AUTH_CHALLENGE
		)
	),
	construct.Padding(1),
	'server_seed' / construct.Int,
	'seed1' / construct.BytesInteger(16),
	'seed2' / construct.BytesInteger(16)

)

