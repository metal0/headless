import construct

from pont_client.utility.construct import PackEnum
from .constants import Response
from pont_client.client.auth.net.packets.constants import Opcode

ResponseHeader = construct.Struct(
	'opcode' / PackEnum(Opcode),
	'response' / construct.Switch(
		construct.this.opcode, {
			Opcode.login_challenge: PackEnum(Response),
			Opcode.login_proof: PackEnum(Response),
			Opcode.realm_list: construct.Pass
		}
	)
)