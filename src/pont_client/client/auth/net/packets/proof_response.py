import construct
from .parse import parser
from .constants import Response, Opcode
from pont_client.utility.construct import ConstructEnum

ProofResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_proof, ConstructEnum(Opcode)), Opcode.login_proof),
	'response' / construct.Default(ConstructEnum(Response), Response.success),

	'session_proof_hash' / construct.BytesInteger(20, swapped=True),
	'account_flags' / construct.Default(construct.Int, 32768),
	'survey_id' / construct.Default(construct.Int, 0),
	'login_flags' / construct.Default(construct.Short, 0)
)

parser.set_parser(Opcode.login_proof, parser=ProofResponse)