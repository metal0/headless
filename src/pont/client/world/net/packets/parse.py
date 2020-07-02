import construct
from typing import Dict, Optional
from .constants import Opcode
from .headers import ServerHeader
from .... import log
log = log.mgr.get_logger(__name__)

class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		log.debug(f'[set_parser] {opcode=}, {parser=}')
		self._parsers[opcode] = parser

	def parse_header(self, data: bytes) -> ServerHeader:
		try:
			return ServerHeader().parse(data)
		except:
			return None

	def parse(self, data: bytes):
		log.debug(f'[WorldPacketParser] {data=}')
		header = ServerHeader().parse(data)

		log.debug(f'[WorldPacketParser.parse] {header=}')
		return self._parsers[header.opcode].parse(data)

parser = WorldPacketParser()