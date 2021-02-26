import construct

from pont.utility.construct import PackEnum
from ..opcode import Opcode
from ..response import Response

def ResponseHeader(opcode=None, response=None):
	if opcode is not None:
		response_con = construct.Pass
		if opcode in [Opcode.login_proof, Opcode.login_challenge]:
			if response is None:
				response = Response.success

			response_con = construct.Default(PackEnum(Response), response)

		return construct.Struct(
			'opcode' / construct.Default(construct.Const(opcode, PackEnum(Opcode)), opcode),
			'response' / response_con
		)

	return construct.Struct(
		'opcode' / PackEnum(Opcode),
		'response' / construct.Switch(
			construct.this.opcode, {
				Opcode.login_challenge: PackEnum(Response),
				Opcode.login_proof: PackEnum(Response),
				Opcode.realm_list: construct.Pass
			}
		)
	)
