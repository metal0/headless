import collections

MockCharacter = collections.namedtuple('MockCharacter', ['name', 'guid'])

MockWorld = collections.namedtuple('MockWorld', ['protocol', 'wait_for_packet', 'emitter'])
MockQueryResponse = collections.namedtuple('MockQueryResponse', ['found', 'info'])
MockNameInfo = collections.namedtuple('MockNameInfo', ['name'])
