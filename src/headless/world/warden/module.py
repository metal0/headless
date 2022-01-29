import os
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
    def __init__(self, size: int, mod_id: Union[bytes, str, int], key: bytes):
        if type(mod_id) is int:
            mod_id = hex(mod_id).replace('0x', '')
        elif type(mod_id) is bytes:
            mod_id = mod_id.hex().replace('0x', '')

        self._mod_id = mod_id
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
        return self._mod_id

def load_crs(path: str):
    with open(path, 'rb') as f:
        cr_size = os.path.getsize(path) - 8
        print(f'{cr_size=} {ChallengeResponse.sizeof()=}')
        if cr_size % ChallengeResponse.sizeof() != 0:
            print('file size is not a multiple of challenge response size')
        return ChallengeResponseFile.parse(f.read())

