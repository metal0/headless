import construct

from pont.utility.construct import PackEnum
from ..response import Response
from ..opcode import Opcode

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