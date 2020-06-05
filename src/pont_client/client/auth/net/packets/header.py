import construct

from pont_client.utility.construct import ConstructEnum
from .constants import Response
from pont_client.client.auth.net.packets.constants import Opcode

ResponseHeader = construct.Struct(
	'opcode' / ConstructEnum(Opcode),
	'response' / construct.Switch(
		construct.this.opcode, {
			Opcode.login_challenge: ConstructEnum(Response),
			Opcode.login_proof: ConstructEnum(Response),
			Opcode.realm_list: None
		}
	)
)