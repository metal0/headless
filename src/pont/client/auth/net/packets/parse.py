import construct

from typing import Dict, Optional

from .header import ResponseHeader
from .constants import Response, Opcode
from pont.client.auth.errors import AuthError
from ....log import mgr
log = mgr.get_logger(__name__)

class AuthPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse(self, packet: bytes):
		header = ResponseHeader.parse(packet)
		opcode: Opcode = header.opcode
		response: Optional[Response] = header.response

		if response is not None and response != Response.success:
			raise AuthError(f'Received error response: {response}')

		parser = self._parsers[opcode]
		if parser is None:
			raise ValueError(f'Decoder not implemented for opcode: {opcode}')

		return parser.parse(packet)

parser = AuthPacketParser()