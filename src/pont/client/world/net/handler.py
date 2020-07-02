from pont.client.world.net.packets import SMSG_AUTH_RESPONSE, SMSG_PONG, SMSG_WARDEN_DATA
from pont.client.world.net.packets.constants import Opcode
from .packets.auth_packets import AuthResponse
from ..errors import ProtocolError
from ... import events, log
log = log.mgr.get_logger(__name__)

class WorldHandler:
	def __init__(self, emitter):
		self._emitter = emitter
		self._packet_map = {
			Opcode.SMSG_AUTH_RESPONSE: self.handle_auth_response,
			Opcode.SMSG_WARDEN_DATA: self.handle_warden_data,
			Opcode.SMSG_PONG: self.handle_pong,
		}

	def handle(self, packet):
		fn = self._packet_map[packet.header.opcode]

		if fn is None:
			log.debug(f'Dropped packet: packet={packet}')
			return

		return self._packet_map[packet.header.opcode](packet)

	def handle_auth_response(self, packet: SMSG_AUTH_RESPONSE):
		self._emitter.emit(events.world.received_SMSG_AUTH_RESPONSE, packet=packet)
		log.debug(f'[handle_auth_response] packet={packet}')
		if packet.response == AuthResponse.ok:
			self._emitter.emit(events.world.logged_in)

		elif packet.response == AuthResponse.wait_queue:
			self._emitter.emit(events.world.in_queue, packet.queue_position)

		else:
			raise ProtocolError(str(packet.response))

	def handle_warden_data(self, packet: SMSG_WARDEN_DATA):
		self._emitter.emit(events.world.received_SMSG_WARDEN_DATA, packet=packet)
		log.debug(f'[handle_warden_data] packet={packet}')

	def handle_pong(self, packet: SMSG_PONG):
		self._emitter.emit(events.world.received_SMSG_PONG, packet=packet)
		log.debug(f'[handle_pong] packet={packet}')
