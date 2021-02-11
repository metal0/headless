from typing import Dict, Optional

import construct

from pont.client.auth.errors import InvalidLogin
from .challenge_response import ChallengeResponse
from .header import ResponseHeader
from .proof_response import ProofResponse
from .realmlist_response import RealmlistResponse
from ..opcode import Opcode
from ..response import Response

def parse_size(data: bytes):
	return construct.Int16ul.parse(data[1:3])

class AuthPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}
		self.set_parser(Opcode.login_challenge, ChallengeResponse)
		self.set_parser(Opcode.login_proof, ProofResponse)
		self.set_parser(Opcode.realm_list, RealmlistResponse)

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse(self, packet: bytes):
		header = ResponseHeader().parse(packet)
		opcode: Opcode = header.opcode
		response: Optional[Response] = header.response

		if response is not None and response != Response.success:
			raise InvalidLogin(f'Received error response: {response}')

		parser = self._parsers[opcode]
		if parser is None:
			raise ValueError(f'Decoder not implemented for opcode: {opcode}')

		return parser.parse(packet)

parser = AuthPacketParser()