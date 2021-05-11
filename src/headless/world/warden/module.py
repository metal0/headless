from typing import Union

import construct
from wlink.cryptography import RC4
from wlink.utility.construct import PackEnum

from headless.world.warden import CheatCheckType

ChallengeResponse = construct.Struct(
    'seed' / construct.BytesInteger(16, swapped=True),
    'reply' / construct.BytesInteger(20, swapped=True),
    'client_key' / construct.BytesInteger(16, swapped=True),
    'server_key' / construct.BytesInteger(16, swapped=True),
)

ChallengeResponseFile = construct.Struct(
    'scan_types' / construct.Array(9, PackEnum(CheatCheckType)),
    'crs' / construct.GreedyRange(ChallengeResponse)
)

class WardenModule:
    def __init__(self, size: int, id: Union[bytes, str, int], key: bytes):
        if type(id) is int:
            id = hex(id).replace('0x', '')
        elif type(id) is bytes:
            id = id.hex().replace('0x', '')

        self._id = id
        self._rc4 = RC4(key=key)
        self._target_size = size
        self._module_bytes = bytearray()

    def new_chunk(self, chunk: bytes):
        self._module_bytes.extend(self.rc4.decrypt(chunk))

    def __len__(self):
        return len(self._module_bytes)

    def completed(self):
        return len(self) == self._target_size

    @property
    def rc4(self):
        return self._rc4

    @property
    def data(self) -> bytes:
        return bytes(self._module_bytes)

    @property
    def id(self):
        return self._id

def load_crs(path: str):
    with open(path, 'rb') as f:
        return ChallengeResponseFile.parse(f.read())


