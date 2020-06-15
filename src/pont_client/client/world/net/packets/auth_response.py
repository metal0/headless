import construct

from pont_client.client.world.net.packets.constants import Opcode, Expansion
from pont_client.utility.construct import PackEnum

SMSG_AUTH_RESPONSE = construct.Struct(
	'size' / construct.Short,
	'opcode' / construct.Const(
		Opcode.SMSG_AUTH_RESPONSE,
		construct.Default(
			construct.ByteSwapped(PackEnum(Opcode, construct.Short)),
			Opcode.SMSG_AUTH_RESPONSE
		),
	),
	'result' / construct.Byte,
	'billing_time_remaining' / construct.Int,
	'billing_plan_flags' / construct.Byte,
	'billing_time_rested' / construct.Int,
	'expansion' / PackEnum(Expansion)
)