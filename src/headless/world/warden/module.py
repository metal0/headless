import construct
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
    def __init__(self):
        # self._module_rc4: Optional[RC4] = None
        self._module_length = 0
        self._module_id = None
        self._module = bytearray()

    @property
    def data(self):
        return self._module


def load_crs(path: str):
    with open(path, 'rb') as f:
        return ChallengeResponseFile.parse(f.read())


