from enum import Enum


class Action(Enum):
    calculate_hash_result = 0


class Emulator:
    def __init__(self, world):
        self._emulations = {}
        self.world = world

    # async def emulate(self, action):


class Emulation:
    def __init__(self):
        pass
