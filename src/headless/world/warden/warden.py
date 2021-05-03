import inspect
from enum import Enum
from typing import Optional

import construct
import trio
from wlink.cryptography import RC4
from wlink.utility.construct import PackEnum

from headless import events
from headless.log import logger
from headless.world.warden import CheatChecksRequest, check
# from headless.world.warden.check import calculate_hash_result
from headless.world.warden.emulate import Emulator
from headless.world.warden.sha1_randx import SHA1Randx

class ServerCommand(Enum):
	module_use = 0
	module_cache = 1
	cheat_checks_request = 26
	module_initialize = 3
	memory_check_request = 4
	hash_request = 5

class ClientCommand(Enum):
	module_missing = 0
	module_ok = 1
	cheat_check_result = 2
	memory_check_result = 3
	hash_result = 4
	module_failed = 5

ServerModuleInfoRequest = construct.Struct(
	'id' / construct.BytesInteger(length=16, swapped=True),
	'key' / construct.BytesInteger(length=16, swapped=True),
	'size' / construct.Int32ul
)

ServerModuleTransfer = construct.Struct(
	'size' / construct.Int16ul,
	'chunk' / construct.Bytes(construct.this.size)
)

ServerModule = construct.Struct(
	'decompressed_length' / construct.Int32ul,
	'module' / construct.Compressed(construct.GreedyBytes, 'zlib')
)

InitModuleRequest = construct.Struct(
	'command1' / construct.Byte,
	'size1' / construct.Int16ul,
	'checksum1' / construct.Int32ul,
	'unk1' / construct.Bytes(2),
	'type' / construct.Byte,
	'string_library1' / construct.Byte,
	'function1' / construct.Array(4, construct.Int32ul),

	'command2' / construct.Byte,
	'size2' / construct.Int16ul,
	'checksum2' / construct.Int32ul,
	'unk2' / construct.Bytes(2),
	'string_library2' / construct.Byte,
	'function2' / construct.Int32ul,
	'function2_set' / construct.Byte,

	'command3' / construct.Byte,
	'size3' / construct.Int16ul,
	'checksum3' / construct.Int32ul,
	'unk3' / construct.Bytes(2),
	'string_library3' / construct.Byte,
	'function3' / construct.Int32ul,
	'function3_set' / construct.Byte,
)

ServerHashRequest = construct.Struct(
	'seed' / construct.BytesInteger(length=16, swapped=True)
)

ClientModule = construct.Struct(
	'id' / construct.BytesInteger(length=16, swapped=True),
	'key' / construct.BytesInteger(length=16, swapped=True),
	'data' / construct.PrefixedArray(construct.Int32ul, construct.Byte)
)

ClientHashResult = construct.Bytes(20)

def ServerWardenData():
	return construct.Struct(
		'command' / PackEnum(ServerCommand),
		'data' / construct.Switch(
			construct.this.command, {
				ServerCommand.module_use: ServerModuleInfoRequest,
				ServerCommand.module_cache: ServerModuleTransfer,
				ServerCommand.cheat_checks_request: CheatChecksRequest,
				ServerCommand.module_initialize: InitModuleRequest,
				ServerCommand.hash_request: ServerHashRequest
			}
		)
	)

ClientWardenData = construct.Struct(
	'command' / PackEnum(ClientCommand),
	'data' / construct.Switch(
		construct.this.command, {
			ClientCommand.module_ok: construct.Pass,
			ClientCommand.module_missing: construct.Pass,
			ClientCommand.hash_result: ClientHashResult,
		}
	)
)

class Warden:
	def __init__(self, world):
		self.world = world
		self._sha1 = SHA1Randx(data=world.session_key)
		self._client_rc4 = RC4(key=self._sha1.generate(16))
		self._server_rc4 = RC4(key=self._sha1.generate(16))
		self._module_rc4: Optional[RC4] = None
		self._module_length = 0
		self._module_id = None
		self._module = bytearray()

		self._opcode_handlers = {
			ServerCommand.module_use: self.handle_module_use,
			ServerCommand.module_cache: self.handle_module_cache,
			ServerCommand.hash_request: self.handle_hash_request,
			ServerCommand.module_initialize: self.handle_module_init,
		}

		self.emulator = Emulator(world)
		self.world.emitter.on(events.world.received_warden_data, self.handle)

	@property
	def module(self):
		return self._module

	@property
	def module_id(self):
		return self._module_id

	def is_enabled(self):
		return self._module_rc4 is not None

	async def send(self, command: ClientCommand, data=None):
		packet = ClientWardenData.build(dict(command=command, data=data))
		encrypted = self._client_rc4.encrypt(packet)
		await self.world.protocol.send_CMSG_WARDEN_DATA(encrypted=encrypted)

	async def handle(self, packet):
		logger.log('PACKETS', f'warden packet: {packet=}')
		decrypted = self._server_rc4.decrypt(packet.encrypted)
		data = ServerWardenData().parse(decrypted)
		logger.log('PACKETS', f'{data=}')

		handler = self._opcode_handlers[data.command]
		if inspect.iscoroutinefunction(handler):
			await handler(data.data)
		else:
			handler(data.data)

	async def handle_module_use(self, data: ServerModuleInfoRequest):
		logger.log('WARDEN', f'Warden module_use request')
		key = int.to_bytes(data.key, 20, 'little')
		if len(self._module) > 0:
			command = ClientCommand.module_ok
		else:
			self._module_rc4 = RC4(key=key)
			self._module_length = data.size
			self._module_id = hex(data.id).replace('0x', '')
			command = ClientCommand.module_missing

		await self.send(command)

	async def handle_module_cache(self, data: ServerModuleTransfer):
		if len(self.module) == 0:
			logger.log('WARDEN', f'Receiving module {self.module_id} from server...')

		self._module.extend(self._module_rc4.decrypt(data.chunk))
		if len(self.module) == self._module_length:
			logger.log('WARDEN', f'Module received ({len(self.module)} bytes)')
			async with await trio.open_file(f'{self.module_id}.bin', 'wb') as f:
				await f.write(self.module)

			await self.send(ClientCommand.module_ok)

	async def handle_hash_request(self, data: ServerHashRequest):
		logger.log('WARDEN', f'{data.seed=}')
		hash, client_key, server_key = check.calculate_hash_result(data.seed, self.module_id)
		logger.log('WARDEN', f'{hash=} {client_key=} {server_key=}')

		self._client_rc4 = RC4(key=client_key)
		self._server_rc4 = RC4(key=server_key)
		await self.send(command=ClientCommand.hash_result, data=ClientHashResult.build(hash))

	async def handle_module_init(self, data):
		logger.log('WARDEN', f'module init: {data=}')
