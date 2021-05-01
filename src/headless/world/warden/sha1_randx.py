import hashlib

class SHA1Randx:
    def __init__(self, data):
        if type(data) is int:
            data = int.to_bytes(data, 40, 'little')

        size = int(len(data) / 2)
        first_half, last_half = (data[:size], data[size:])

        self._o1 = hashlib.sha1(first_half).digest()
        self._o2 = hashlib.sha1(last_half).digest()
        self._o0 = bytes([0] * 20)
        self._taken = 0
        self._fill_up()

    def generate(self, size):
        result = bytearray()
        for i in range(size):
            if self._taken == 20:
                self._fill_up()

            result.append(self._o0[self._taken])
            self._taken += 1

        return bytes(result)

    def _fill_up(self):
        hash = hashlib.sha1()
        hash.update(self._o1)
        hash.update(self._o0)
        hash.update(self._o2)

        self._o0 = hash.digest()
        self._taken = 0
