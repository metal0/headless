import datetime

import construct

from pont.utility.construct import AddressPort, GuidUnpacker, PackedCoordinates, unpack_guid, pack_guid, PackedDateTime
from pont.client.world import Position
from pont.client.world.guid import Guid, GuidType


def test_address_port():
	# Test big endian encoding and decoding
	con = AddressPort()
	address = ('127.0.0.1', 8085)
	address_packed = con.build(address)

	assert address_packed == b'127.0.0.1:8085\x00'
	assert ('127.0.0.1', 8085) == con.parse(address_packed)

def test_address_port2():
	# Test composability with other constructs
	addr_con = AddressPort()
	Test = construct.Sequence(
		construct.CString('ascii'),
		addr_con,
		construct.Int
	)

	data = Test.build(['hey there', ('127.0.0.1', 8085), 7])
	assert data  == b'hey there\x00127.0.0.1:8085\x00\x00\x00\x00\x07'
	assert Test.parse(data) == ['hey there', ('127.0.0.1', 8085), 7]

def test_packed_guid():
	guid = Guid(value=0x7000000003372cc)
	assert unpack_guid(*pack_guid(guid.value)) == guid.value

	packed_guid = GuidUnpacker(Guid).build(guid)
	parsed_guid = GuidUnpacker(Guid).parse(packed_guid)
	assert parsed_guid == guid

	guid = Guid(counter=3, high=7)
	repacked_guid = Guid(value=unpack_guid(*pack_guid(guid.value)))
	assert repacked_guid.counter == 3
	assert repacked_guid.high == 7

	guid2 = Guid(counter=32, type=GuidType.unit)
	repacked_guid2 = Guid(value=unpack_guid(*pack_guid(guid2.value)))
	assert repacked_guid2.counter == 32
	assert repacked_guid2.type == GuidType.unit

# TODO: fix
def test_packed_time():
	time = datetime.datetime(2021, 1, 3, 5, 39)

	print(f'{time=}')
	packed_time = PackedDateTime().build(time)

	print(f'{packed_time=}')
	parsed_time = PackedDateTime().parse(packed_time)
	print(f'{parsed_time=}')

	assert time == parsed_time
	# guid = Guid(value=0x7000000003372cc)
	#
	# print(guid)
	# print(Guid(value=unpack_guid(*pack_guid(guid.value))))
	# assert unpack_guid(*pack_guid(guid.value)) == guid.value
	#
	# packed_guid = GuidUnpacker(Guid).build(guid)
	# parsed_guid = GuidUnpacker(Guid).parse(packed_guid)
	# assert parsed_guid == guid

def test_packed_coordinates():
	pos = Position(2.1, -33, 99.8)
	data = PackedCoordinates(Position).build(pos)
	packet = PackedCoordinates(Position).parse(data)
	print(packet)

	assert packet.x == 2
	assert packet.y == (2**9 - 33) # Can't distinguish between negatives it seems
	assert packet.z == 99.75

	pos = Position(0, 1, 3)
	data = PackedCoordinates(Position).build(pos)
	packet = PackedCoordinates(Position).parse(data)
	print(packet)

	assert packet.x == 0
	assert packet.y == 1
	assert packet.z == 3

