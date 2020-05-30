import construct
from pont import utility
from pont.client.auth import Opcode
from pont.client.auth.packets.constants import Response

ResponseHeader = construct.Struct(
	'opcode' / utility.construct.ConstructEnum(Opcode),
	'response' / construct.Switch(
		construct.this.opcode, {
			Opcode.login_challenge: Response,
			Opcode.login_proof: Response,
			Opcode.realm_list: None
		}
	)
)