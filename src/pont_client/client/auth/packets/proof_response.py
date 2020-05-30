import construct
from .constants import Response, Opcode, opcodes
from pont.client.auth.packets.parse import parser
from pont.utility.construct import BigInt

ProofResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_proof, Opcode), opcodes.login_proof),
	'response' / construct.Default(Response, Response.success),

	'session_proof_hash' / BigInt(20),
	'account_flags' / construct.Default(construct.Int, 32768),
	'survey_id' / construct.Default(construct.Int, 0),
	'login_flags' / construct.Default(construct.Short, 0)
)

parser.set_parser(opcodes.login_proof, parser=ProofResponse)