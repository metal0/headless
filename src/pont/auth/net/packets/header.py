import construct

from pont.utility.construct import PackEnum
from ..opcode import Opcode
from ..response import Response

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