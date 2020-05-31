import construct
from .parse import parser
from .constants import Response, Opcode, opcodes
from ....utility.construct import BigInt, ConstructEnum

ProofResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(opcodes.login_proof, ConstructEnum(Opcode)), opcodes.login_proof),
	'response' / construct.Default(ConstructEnum(Response), Response.success),

	'session_proof_hash' / BigInt(20),
	'account_flags' / construct.Default(construct.Int, 32768),
	'survey_id' / construct.Default(construct.Int, 0),
	'login_flags' / construct.Default(construct.Short, 0)
)

parser.set_parser(opcodes.login_proof, parser=ProofResponse)