import collections
from wlink.log import logger

from headless.utility.emitter import BaseEmitter

def GenericMemoryEmitter(emitter_type):
	class _MemoryEmitter(emitter_type):
		Memory = collections.namedtuple('Memory', ['args', 'kwargs'])

		def __init__(self, emitter=None, nursery=None, scope=None):
			super().__init__(emitter=emitter, nursery=nursery, scope=scope)
			self.memory = {}

		def emit(self, event, *args, **kwargs):
			logger.log('EVENTS', f'{event=}, {kwargs}')
			super().emit(event, *args, **kwargs)
			if event in self.memory.keys():
				self.memory[event].append(_MemoryEmitter.Memory(args=args, kwargs=kwargs))
			else:
				self.memory[event] = [_MemoryEmitter.Memory(args=args, kwargs=kwargs)]
	return _MemoryEmitter

MemoryEmitter = GenericMemoryEmitter(BaseEmitter)
