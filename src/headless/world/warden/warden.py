import inspect
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Callable, NamedTuple

import construct
import trio
from wlink.cryptography import RC4
from wlink.utility.construct import PackEnum
from wlink.world.packets import make_CMSG_WARDEN_DATA, CMSG_WARDEN_DATA

from headless import events
from headless.log import logger
from headless.world.warden import CheatChecksRequest, check
from headless.world.warden.cr import ChallengeResponseCache
from headless.world.warden.emulate import Emulator
from headless.world.warden.error import ChallengeResponseNotFound
from headless.world.warden.module import WardenModule
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
    "id" / construct.Bytes(16), "key" / construct.Bytes(16), "size" / construct.Int32ul
)

ServerModuleTransfer = construct.Struct(
    "size" / construct.Int16ul, "chunk" / construct.Bytes(construct.this.size)
)

ServerModule = construct.Struct(
    "decompressed_length" / construct.Int32ul,
    "module" / construct.Compressed(construct.GreedyBytes, "zlib"),
)

InitModuleRequest = construct.Struct(
    "command1" / construct.Byte,
    "size1" / construct.Int16ul,
    "checksum1" / construct.Int32ul,
    "unk1" / construct.Bytes(2),
    "type" / construct.Byte,
    "string_library1" / construct.Byte,
    "function1" / construct.Array(4, construct.Int32ul),
    "command2" / construct.Byte,
    "size2" / construct.Int16ul,
    "checksum2" / construct.Int32ul,
    "unk2" / construct.Bytes(2),
    "string_library2" / construct.Byte,
    "function2" / construct.Int32ul,
    "function2_set" / construct.Byte,
    "command3" / construct.Byte,
    "size3" / construct.Int16ul,
    "checksum3" / construct.Int32ul,
    "unk3" / construct.Bytes(2),
    "string_library3" / construct.Byte,
    "function3" / construct.Int32ul,
    "function3_set" / construct.Byte,
)

ServerHashRequest = construct.Bytes(16)

ClientModule = construct.Struct(
    "id" / construct.BytesInteger(length=16, swapped=True),
    "key" / construct.BytesInteger(length=16, swapped=True),
    "data" / construct.PrefixedArray(construct.Int32ul, construct.Byte),
)

ClientHashResult = construct.Bytes(20)


def ServerWardenAction():
    return construct.Struct(
        "command" / PackEnum(ServerCommand),
        "data"
        / construct.Switch(
            construct.this.command,
            {
                ServerCommand.module_use: ServerModuleInfoRequest,
                ServerCommand.module_cache: ServerModuleTransfer,
                ServerCommand.cheat_checks_request: CheatChecksRequest,
                ServerCommand.module_initialize: InitModuleRequest,
                ServerCommand.hash_request: ServerHashRequest,
            },
        ),
    )


ClientWardenData = construct.Struct(
    "command" / PackEnum(ClientCommand),
    "data"
    / construct.Switch(
        construct.this.command,
        {
            ClientCommand.module_ok: construct.Pass,
            ClientCommand.module_missing: construct.Pass,
            ClientCommand.hash_result: ClientHashResult,
            # ClientCommand.cheat_check_result:
            # ClientCommand.memory_check_result:
        },
    ),
)


class Warden:
    def __init__(self, world, cr_files_path: Path):
        self.world = world
        self.cr_cache = ChallengeResponseCache(crs_path=cr_files_path)
        self._sha1 = SHA1Randx(data=world.session_key)
        self._client_rc4 = RC4(key=self._sha1.generate(16))
        self._server_rc4 = RC4(key=self._sha1.generate(16))

        self._module = None
        self._opcode_handlers: Dict[ServerCommand, Callable] = {
            ServerCommand.module_use: self.handle_module_use,
            ServerCommand.module_cache: self.handle_module_cache,
            ServerCommand.hash_request: self.handle_hash_request,
            ServerCommand.module_initialize: self.handle_module_init,
            ServerCommand.cheat_checks_request: self.handle_check_checks_request,
            ServerCommand.memory_check_request: self.handle_memory_checks_request,
        }

        self.emulator = Emulator(world)
        self._handler_task = self.world.emitter.on(
            events.world.received_warden_data, self.handle
        )

    def __del__(self):
        self.world.emitter.remove_listener(
            events.world.received_warden_data, self.handle
        )

    @property
    def module(self) -> Optional[WardenModule]:
        return self._module

    @property
    def module_id(self):
        return self.module.id if self.module else None

    def enabled(self):
        return self.module is not None and self.module.completed()

    async def send(self, command: ClientCommand, data=None):
        packet = ClientWardenData.build(dict(command=command, data=data))
        logger.log("PACKETS", f"send warden packet: {packet=}")
        encrypted = self._client_rc4.encrypt(packet)
        await self.world.stream.send_encrypted_packet(
            CMSG_WARDEN_DATA, make_CMSG_WARDEN_DATA(encrypted=encrypted)
        )

    async def handle(self, packet):
        logger.log("PACKETS", f"warden packet: {packet=}")
        decrypted = self._server_rc4.decrypt(packet.encrypted)
        logger.log("PACKETS", f"warden packet: {decrypted=}")
        warden_data = ServerWardenAction().parse(decrypted)
        logger.log("PACKETS", f"{warden_data=}")

        handler = self._opcode_handlers[warden_data.command]
        if inspect.iscoroutinefunction(handler):
            await handler(warden_data.data)
        else:
            handler(warden_data.data)

    async def handle_module_use(self, request: ServerModuleInfoRequest):
        logger.log(
            "WARDEN",
            f"Downloading module: {request.size=} {request.id.hex()=} {request.key.hex()=}",
        )
        if self.enabled():
            command = ClientCommand.module_ok
        else:
            self._module = WardenModule(
                size=request.size, mod_id=request.id, key=request.key
            )
            command = ClientCommand.module_missing

        await self.send(command)

    async def handle_module_cache(self, request: ServerModuleTransfer):
        if len(self.module) == 0:
            logger.log("WARDEN", f"Receiving module {self.module.id} from server...")

        self.module.new_chunk(request.chunk)
        if self.module.completed():
            logger.log("WARDEN", f"Module received ({len(self.module)} bytes)")
            async with await trio.open_file(f"/tmp/warden_modules/{self.module.id}.bin", "wb") as f:
                await f.write(self.module.data)

            await self.send(ClientCommand.module_ok)

    async def handle_hash_request(self, seed: int):
        logger.log("WARDEN", f"{self.module.id=} {seed=}")
        cr = await self.cr_cache.fetch((self.module.id, seed))
        if cr is None:
            raise ChallengeResponseNotFound(
                f"CR not found for ({self.module.id}, {seed})"
            )

        self._client_rc4 = RC4(key=cr.client_key)
        self._server_rc4 = RC4(key=cr.server_key)

        hash_result = ClientHashResult.parse(ClientHashResult.build(cr.reply))
        await self.send(command=ClientCommand.hash_result, data=hash_result)

        logger.log("WARDEN", f"Responded with: {cr=}")
        return cr

    async def handle_module_init(self, data):
        logger.log("WARDEN", f"module init: {data=}")

    async def handle_check_checks_request(self, data):
        logger.log("WARDEN", f"{data=}")

    async def handle_memory_checks_request(self, data):
        logger.log("WARDEN", f"{data=}")
