from pont.client.auth.net import packets
from pont.client.auth.realm import RealmType, RealmStatus, RealmFlags, Realm

def  test_realmlist_response_decode_encode():
	packet = bytes.fromhex('108700000000000300010000426c61636b726f636b205b507650206f6e6c795d0035342e33362e3130352e3134373a38303836000000000008080a01000049636563726f776e0035342e33362e3130352e3134383a3830383500000040400a08070100004c6f72646165726f6e0035342e33362e3130352e3134363a393432370000000040030806')
	realmlist_response = packets.RealmlistResponse.parse(packet)
	print(f'{realmlist_response.packet_size=}')
	assert len(realmlist_response.realms) == 3
	assert realmlist_response.realms[0].name == 'Blackrock [PvP only]'
	assert realmlist_response.realms[0].type == RealmType.pvp
	assert realmlist_response.realms[0].status == RealmStatus.online
	# assert realmlist_response.realms[0].population == RealmPopulation.low
	assert realmlist_response.realms[0].flags == RealmFlags.none
	assert realmlist_response.realms[0].address == ('54.36.105.147', 8086)
	assert realmlist_response.realms[0].num_characters == 8
	assert realmlist_response.realms[0].timezone == 8

	assert realmlist_response.realms[1].name == 'Icecrown'
	assert realmlist_response.realms[1].type == RealmType.pvp
	assert realmlist_response.realms[1].status == RealmStatus.online
	# assert realmlist_response.realms[1].population == RealmPopulation.high
	assert realmlist_response.realms[1].flags == RealmFlags.none
	assert realmlist_response.realms[1].address == ('54.36.105.148', 8085)
	assert realmlist_response.realms[1].num_characters == 10
	assert realmlist_response.realms[1].timezone == 8

	assert realmlist_response.realms[2].name == 'Lordaeron'
	assert realmlist_response.realms[2].type == RealmType.pvp
	assert realmlist_response.realms[2].status == RealmStatus.online
	# assert realmlist_response.realms[2].population == RealmPopulation.medium
	assert realmlist_response.realms[2].flags == RealmFlags.none
	assert realmlist_response.realms[2].address == ('54.36.105.146', 9427)
	assert realmlist_response.realms[2].num_characters == 3
	assert realmlist_response.realms[2].timezone == 8

	packet2 = packets.RealmlistResponse.build(realmlist_response)
	assert packet == packet2
