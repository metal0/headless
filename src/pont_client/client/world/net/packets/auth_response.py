import construct

from pont_client.client.world.net.packets import parser
from pont_client.client.world.net.packets.constants import Opcode, Expansion
from pont_client.client.world.net.packets.headers import ServerHeader
from pont_client.utility.construct import PackEnum

SMSG_AUTH_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_RESPONSE, 1 + 4 + 1 + 4 + 1 + 4),
	'extended' / construct.Byte,
	'billing_time_remaining' / construct.ByteSwapped(construct.Int),
	'billing_plan_flags' / construct.Byte,
	'billing_time_rested' / construct.ByteSwapped(construct.Int),
	'expansion' / PackEnum(Expansion),
	'queue_position' / construct.Switch(
		construct.this.extended, {
			True: construct.ByteSwapped(construct.Int),
			False: construct.Pass
		}
	)
)

parser.set_parser(Opcode.SMSG_AUTH_RESPONSE, SMSG_AUTH_RESPONSE)