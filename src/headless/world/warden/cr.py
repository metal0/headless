from pathlib import Path
from typing import Union, Tuple

import construct
import trio
from ...utility.cache import Cache
from ...log import logger

ChallengeResponse = construct.Struct(
    'seed' / construct.Bytes(16),
    'reply' / construct.Bytes(20),
    'client_key' / construct.Bytes(16),
    'server_key' / construct.Bytes(16),
)

ChallengeResponseFile = construct.Struct(
    'memread_offset' / construct.Int32ul,
    'pageread_offset' / construct.Int32ul,
    construct.Padding(9),
    # 'scan_types' / construct.Array(9, PackEnum(CheatCheckType)),
    'crs' / construct.GreedyRange(ChallengeResponse)
)

class ChallengeResponseCache(Cache):
    def __init__(self, crs_path: Path):
        super().__init__()
        self.crs_path = crs_path

    async def fetch(self, key: Tuple[str, bytes]):
        (id, seed) = key
        logger.trace(f'{id=} {seed=}')
        path = self.crs_path.joinpath(f'{id}.cr')
        logger.debug(f'{path=}')

        if (id, seed) == ('79C0768D657977D697E10BAD956CCED1', b'M\x80\x8d,w\xd9\x05\xc4\x1ac\x80\xec\x08Xj\xfe'):
            return ChallengeResponse.parse(ChallengeResponse.build(dict(
                seed=seed,
                reply=b'V\x8c\x05Lx\x1a\x97*`7\xa2)\x0c"\xb5%q\xa0oN',
                client_key=b'\x7f\x96\xee\xfd\xa5\xb6= \xa4\xdf\x8e\x00\xcb\xf4\x83\x04',
                server_key=b'\xc2\xb7\xad\xed\xfc\xcc\xa9\xc2\xbf\xb3\xf8V\x02\xba\x80\x9b'
            )))

        async with await trio.open_file(path, mode='rb') as f:
            data = await f.read()
            try:
                cr_file = ChallengeResponseFile.parse(data)
                for cr in cr_file.crs:
                    if cr.seed == seed:
                        logger.trace(f'{cr=}')
                        return cr
            except Exception as e:
                print(e)
        return None


__all__ = [
    'ChallengeResponseFile', 'ChallengeResponseCache', 'ChallengeResponse'
]