import trio

from pont_client.client import log
from pont_client.client.world.net import packets

log = log.get_logger(__name__)

class WorldProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()

	async def send_SMSG_AUTH_CHALLENGE(self, server_seed, encryption_seed1, encryption_seed2):
		async with self._send_lock:
			packet = packets.SMSG_AUTH_CHALLENGE.build({
				'server_seed': server_seed,
				'encryption_seed1': encryption_seed1,
				'encryption_seed2': encryption_seed2,
			})

			await self.stream.send_all(packet)

	async def receive_SMSG_AUTH_CHALLENGE(self) -> packets.SMSG_AUTH_CHALLENGE:
		async with self._read_lock:
			packet = await self.stream.receive_some()
			log.debug(f'[receive_SMSG_CHAR_ENUM] received: {packet}')
			return packets.parser.parse(packet)

	async def send_CMSG_AUTH_SESSION(self, account_name, client_seed, account_hash, realm_id, server_seed = None,
		build=12340, login_server_id=0, login_server_type=0, region_id=0, battlegroup_id=0):
		async with self._send_lock:
			# if not server_seed is None:

			packet = packets.CMSG_AUTH_SESSION.build({
				'build': build,
				'login_server_id': login_server_id,
				'account_name': account_name,
				'login_server_type': login_server_type,
				'client_seed': client_seed,
				'region_id': region_id,
				'battlegroup_id': battlegroup_id,
				'realm_id': realm_id,
				'account_hash': account_hash,
				'header': {'size': 61 + 237 + len(account_name)}
			})

			log.debug(f'[send_CMSG_AUTH_SESSION] {packet=}')
			log.debug(f'[send_CMSG_AUTH_SESSION] {packets.CMSG_AUTH_SESSION.parse(packet)}')
			await self.stream.send_all(packet)

	async def receive_CMSG_AUTH_SESSION(self):
		async with self._read_lock:
			packet = await self.stream.receive_some()
			return packets.CMSG_AUTH_SESSION.parse(packet)

	async def send_CMSG_CHAR_ENUM(self):
		async with self._send_lock:
			packet = packets.CMSG_CHAR_ENUM.build()
			await self.stream.send_all(packet)
			log.debug(f'[send_CMSG_CHAR_ENUM] sent: {packet}')

	async def receive_SMSG_CHAR_ENUM(self) -> packets.SMSG_CHAR_ENUM:
		async with self._read_lock:
			packet = await self.stream.receive_some()
			log.debug(f'[receive_SMSG_CHAR_ENUM] received: {packet}')
			return packets.parser.parse(packet)

	async def send_CMSG_PING(self):
		async with self._send_lock:
			packet = packets.CMSG_PING.build({})
			await self.stream.send_all(packet)
			log.debug(f'[send_CMSG_PING] sent: {packet}')

	async def send_CMSG_KEEP_ALIVE(self):
		async with self._send_lock:
			packet = packets.CMSG_KEEP_ALIVE.build({})
			await self.stream.send_all(packet)
			log.debug(f'[send_CMSG_KEEP_ALIVE] sent: {packet}')

	async def receive_packet(self):
		async with self._read_lock:
			return await self.stream.receive_some()

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
