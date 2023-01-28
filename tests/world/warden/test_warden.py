from pathlib import Path
from typing import NamedTuple

import trio
from wlink.world import WorldClientStream

from headless.world.warden import Warden
from headless.world.warden.warden import (
    ServerWardenAction,
    ServerCommand,
    ServerHashRequest,
)
from tests.mock.emitter import MemoryEmitter
from tests.mock.world import MockWorld
from tests.utility.test_cache import mock_wait_for_packet


async def check_hash_request(data):
    async with trio.open_nursery() as n:
        (client_stream, server_stream) = trio.testing.memory_stream_pair()
        session_key = 1545219019590327411168717249486681575835271816005656129138288524658674564194171328330647643695244

        client = WorldClientStream(client_stream, session_key=session_key)
        world = MockWorld(
            stream=client,
            wait_for_packet=mock_wait_for_packet,
            emitter=MemoryEmitter(nursery=n),
            session_key=session_key,
        )

        warden = Warden(world, cr_files_path=Path("/home/fure/repos/warden_modules"))

        class MockModule(NamedTuple):
            id: str

        warden._module = MockModule(id=data["mod_id"])
        action = ServerWardenAction().parse(data["decrypted"])
        print(f"{action=}")

        assert action.command == ServerCommand.hash_request
        cr = await warden.handle_hash_request(action.data)
        print(f"{cr=}")
        assert cr.seed == data["seed"]


async def test_warden_hash_request():
    hash_request_data = [
        dict(
            mod_id="0DBBF209A27B1E279A9FEC5C168A15F7",
            seed=b"\x14\xde\xfd\xdb}\x14F\x81R\x84k\xf2\x965&\x9a",
            decrypted=b"\x05\x14\xde\xfd\xdb}\x14F\x81R\x84k\xf2\x965&\x9a",
        ),
        # dict(
        #     mod_id='79C0768D657977D697E10BAD956CCED1',
        #     seed=b'M\x80\x8d,w\xd9\x05\xc4\x1ac\x80\xec\x08Xj\xfe',
        #     # client_key=bytes([0x7F, 0x96, 0xEE, 0xFD, 0xA5, 0xB6, 0x3D, 0x20, 0xA4, 0xDF, 0x8E, 0x00, 0xCB, 0xF4, 0x83, 0x04]),
        #     decrypted=b'\x05M\x80\x8d,w\xd9\x05\xc4\x1ac\x80\xec\x08Xj\xfe'
        # ),
    ]

    for data in hash_request_data:
        await check_hash_request(data)
