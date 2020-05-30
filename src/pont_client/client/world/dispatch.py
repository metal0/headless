import struct
from pont.client.world.opcode import Opcode
from typing import Dict, Callable, Optional

from pont import log
log = log.get_logger(__name__)

class InvalidPacket(Exception):
	pass

decoders: Dict[Opcode, Optional[Callable]] = {}
for opcode in Opcode:
	decoders[opcode] = None

def set_decoder(opcode: Opcode, decoder):
	decoders[opcode] = decoder

def parse_opcode(packet_data: bytes, pos = 0):
	return Opcode(struct.unpack('<b', packet_data[pos:pos + 1])[0])

def decode(data: bytes):
	opcode = parse_opcode(packet_data=data)
	decoder = decoders[opcode]
	if decoder is None:
		raise ValueError(f'Decoder not implemented for opcode: {opcode}')

	return decoder(raw_bytes=data)
