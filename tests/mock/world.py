import collections

MockCharacter = collections.namedtuple('TestCharacter', ['name'])
MockWorld = collections.namedtuple('TestWorld', ['protocol', 'wait_for_packet'])
MockQueryResponse = collections.namedtuple('MockQueryResponse', ['found', 'info'])
MockNameInfo = collections.namedtuple('MockNameInfo', ['name'])