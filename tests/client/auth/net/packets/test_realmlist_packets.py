from pont.client.auth.net import packets
from pont.client.auth.realm import RealmType, RealmStatus, RealmFlags

def test_realmlist_response_decode_encode():
	data = b'\x10\x87\x00\x00\x00\x00\x00\x03\x00\x01\x00\x00Blackrock [PvP only]\x0054.36.105.147:8086\x00\x00\x00\x00\x00\x08\x08\n\x01\x00\x00Icecrown\x0054.36.105.148:8085\x00\x00\x00@@\n\x08\x07\x01\x00\x00Lordaeron\x0054.36.105.146:9427\x00\x00\x00\x00@\x03\x08\x06'
	realmlist_response = packets.RealmlistResponse.parse(data)
	assert len(realmlist_response.realms) == 3

	calculated_size = 8
	for realm in realmlist_response.realms:
		calculated_size += 3 + len(realm.name) + 1 + len(':'.join(map(str, realm.address))) + 1 + 4 + 3
		if (realm.flags & RealmFlags.specify_build) == RealmFlags.specify_build.value:
			calculated_size += 5

	assert realmlist_response.size == calculated_size
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
	assert packets.RealmlistResponse.build(realmlist_response) == data


	# With build info specified
	data2 = b'\x10g\x00\x00\x00\x00\x00\x02\x00\x01\x00\x04Frosthold\x0051.91.152.139:19090\x00\x00\x00\x00\x00\x01\x05\x04\x03\x03\x0540\x01\x00\x04Frosthold Proxy\x0046.29.17.245:47212\x00\x00\x00\x00\x00\x00\x05\n\x03\x03\x0540\x10\x00'
	response2 = packets.RealmlistResponse.parse(data2)

	assert response2.realms[0].type == RealmType.pvp
	assert response2.realms[0].status == RealmStatus.online
	assert response2.realms[0].flags == RealmFlags.specify_build
	assert response2.realms[0].address == ('51.91.152.139', 19090)
	assert response2.realms[0].name == 'Frosthold'
	assert response2.realms[0].num_characters == 1
	assert response2.realms[0].timezone == 5
	assert response2.realms[0].id == 4
	assert response2.realms[0].build_info.major == 3
	assert response2.realms[0].build_info.minor == 3
	assert response2.realms[0].build_info.bugfix == 5
	assert response2.realms[0].build_info.build == 12340

	assert response2.realms[1].type == RealmType.pvp
	assert response2.realms[1].status == RealmStatus.online
	assert response2.realms[1].flags == RealmFlags.specify_build
	assert response2.realms[1].address == ('46.29.17.245', 47212)
	assert response2.realms[1].name == 'Frosthold Proxy'
	assert response2.realms[1].num_characters == 0
	assert response2.realms[1].timezone == 5
	assert response2.realms[1].id == 10
	assert response2.realms[1].build_info.major == 3
	assert response2.realms[1].build_info.minor == 3
	assert response2.realms[1].build_info.bugfix == 5
	assert response2.realms[1].build_info.build == 12340
