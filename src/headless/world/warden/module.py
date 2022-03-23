from typing import Union

from wlink.cryptography import RC4

class WardenModule:
    # signature_size = 260
    # key_size = 16
    # scan_type_count = 9

    def __init__(self, size: int, mod_id: Union[bytes, str, int], key: bytes):
        print(f'{mod_id=}')
        if type(mod_id) is int:
            self._mod_id = hex(mod_id).replace('0x', '').upper()
        elif type(mod_id) is bytes:
            self._mod_id = mod_id.hex().replace('0x', '').upper()
        else:
            self._mod_id = mod_id.replace('0x', '').upper()

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

