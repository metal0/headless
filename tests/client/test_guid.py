from pont.client.world.guid import Guid, GuidType

def test_guid():
	guid = Guid(counter=3, high=7)
	print(guid)

	assert guid.counter == 3
	assert guid.high == 7
	assert guid.type == GuidType.player

	guid.counter = 16
	guid.high = 37
	assert guid.high == 37
	assert guid.counter == 16
	assert guid.type == GuidType.player
	assert guid.has_entry()

	guid = Guid(counter=32, type=GuidType.unit)
	print(guid)

	assert guid.counter == 32
	assert guid.type == GuidType.unit
	assert not guid.has_entry()

	guid.type = GuidType.item
	print(guid)

	assert guid.type == GuidType.item
	guid.high = GuidType.dynamic_object.value
	print(guid)

	assert guid.has_entry()
	assert guid.type == GuidType.dynamic_object

	guid.high = GuidType.corpse.value
	assert guid.type == GuidType.corpse
	assert guid.has_entry()

def test_guid2():
	guid = Guid(value=0x7000000003372cc)
	assert guid.type == GuidType.player
	assert guid.counter == 0x3372cc
	assert guid.has_entry()

	guid = Guid(counter=1, type=GuidType.player)
	assert guid.counter == 1
	assert guid.type == GuidType.player

