# import trio
#
# import pont.client.auth.packets
# import pont.cryptography.srp
#
# from pont import events, log
# from pont.client.auth.packets.parse import AuthError
# from pont.utility.scoped_emitter import ScopedEmitter
# from pont.utility.string import bytes_to_int
# from typing import Optional
#
# log = log.get_logger(__name__)
#
# _opcode_event_map = {
# 	pont.client.auth.opcodes.login_challenge: events.auth.received_challenge_response,
# 	pont.client.auth.opcodes.login_proof: events.auth.received_proof_response,
# 	pont.client.auth.opcodes.realm_list: events.auth.received_realmlist_response,
# }
#
# class AuthHandler(ScopedEmitter):
# 	def __init__(self, context, emitter):
# 		super().__init__(emitter)
# 		self.__stream: Optional[trio.SocketStream] = None
# 		self.__stream_event = trio.Event()
# 		self.__context = context
# 		self.__client_public = 0
# 		self.session_key = None
# 		self.__session_proof = 0
# 		self.__session_proof_hash = 0
#
# 	def __handle_account_error(self, error_data):
# 		if error_data is not None:
# 			exc = error_data[1]
# 			error = error_data[0]
#
# 			if error == pont.client.auth.errors.unknown_account:
# 				self.emit(events.auth.invalid_login)
# 				raise AuthError('Invalid username or password')
#
# 	async def __ensure_stream_integriy(self):
# 		with trio.fail_after(5):
# 			while True:
# 				await trio.hazmat.checkpoint()
# 				if self.__stream_event.is_set():
# 					break
#
# 	def install(self):
# 		@self.on(events.auth.connected)
# 		def on_connected(stream):
# 			log.debug(f'stream obtained: {stream}')
# 			self.__stream = stream
# 			self.__stream_event.set()
#
# 		@self.on(events.auth.data_received)
# 		async def handle_packet(data: bytes):
# 			await self.__ensure_stream_integriy()
# 			opcode = pont.client.auth.packets.parse.parse_opcode(data=data)
# 			if opcode in _opcode_event_map:
# 				packet = None
# 				error_data = None
# 				try:
# 					await trio.hazmat.checkpoint()
# 					packet = pont.client.auth.packets.parse.parse(packet=data)
# 					log.debug(f'packet received: {opcode} {data}')
#
# 				except (pont.client.auth.packets.parse.InvalidPacket, pont.client.auth.packets.parse.AuthError) as e:
# 					log.debug(f'Packet data: {data}')
# 					error_data = (pont.client.auth.packets.parse.parse_error(data), e)
# 					await trio.hazmat.checkpoint()
#
# 				self.emit(_opcode_event_map[opcode], packet=packet, error_data=error_data)
#
# 			else:
# 				log.debug(f'Packet dropped: {opcode}: {data}')
#
# 		@self.on(event=events.auth.received_challenge_response)
# 		async def handle_challenge_response(packet: pont.client.auth.packets.ChallengeResponse, error_data=None):
# 			log.debug(f'[+] Response: {str(packet)}')
# 			self.__handle_account_error(error_data)
#
# 			srp_client = pont.cryptography.srp.WowSrpClient(
# 				username=self.__context.config.username,
# 				password=self.__context.config.password,
# 				prime=packet.prime,
# 				generator=packet.generator,
# 			)
#
# 			# checksum = wow.auth.cryptography.generate_crc(client_public=srp_client.client_public, crc_salt=response.checksum_salt)
# 			checksum = 0
#
# 			srp_client.process(server_public=packet.server_public, salt=packet.salt)
# 			log.debug('[+] Sending request for proof...')
# 			proof = pont.client.auth.packets.ProofRequest(
# 				client_public=srp_client.client_public,
# 				session_proof=srp_client.session_proof,
# 				checksum=checksum,
# 			)
#
# 			self.session_key = srp_client.session_key
# 			self.__session_proof_hash = bytes_to_int(srp_client.session_proof_hash)
# 			await self.__stream.send_all(proof.encode())
#
# 		@self.on(event=events.auth.received_proof_response)
# 		async def handle_proof_response(packet: pont.client.auth.packets.ProofResponse, error_data=None):
# 			log.debug(f'[+] Response: {packet}')
# 			self.__handle_account_error(error_data)
#
# 			# Compare server and client proofs to see if login was successful
# 			if self.__session_proof_hash == packet.session_proof_hash:
# 				self.emit(events.auth.login_success)
# 			else:
# 				self.emit(events.auth.invalid_login)
#
# 		@self.on(event=events.auth.received_realmlist_response)
# 		def handle_realmlist_response(packet: pont.client.auth.packets.RealmlistResponse, error_data=None):
# 			log.debug(f'[+] Response: {packet}')
# 			self.__handle_account_error(error_data)
# 			self.__realm_list = packet.realms
# 			self.emit(events.auth.realmlist_ready, realmlist=self.__realm_list)
#
