import collections

MockCharacter = collections.namedtuple('MockCharacter', ['name', 'guid'])

MockWorld = collections.namedtuple('MockWorld', ['stream', 'wait_for_packet', 'emitter', 'session_key'])
MockQueryResponse = collections.namedtuple('MockQueryResponse', ['found', 'info'])
MockNameInfo = collections.namedtuple('MockNameInfo', ['name'])
