import construct
from typing import Dict, Optional
from .constants import Opcode
from .headers import ServerHeader
from .... import log

log = log.get_logger(__name__)

class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}
		self._encryption = None

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse_header(self, packet: bytes) -> ServerHeader:
		return ServerHeader().parse(packet)

	def parse(self, packet: bytes):
		log.debug(f'[WorldPacketParser] {packet=}')
		header = ServerHeader().parse(packet)

		log.debug(f'[WorldPacketParser.parse] {header=}')
		return self._parsers[header.opcode].parse(packet)

parser = WorldPacketParser()