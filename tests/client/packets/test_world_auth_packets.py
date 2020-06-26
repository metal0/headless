import random

from pont_client.client import world

def test_world_auth_packet():
	data = bytes.fromhex('002aec01010000004c6f82e4ab892d3d480a9898d510f879f862479fad62c8815ff00fd85e5ab6b4031684e9')
	auth_challenge = world.net.packets.SMSG_AUTH_CHALLENGE.parse(data)
	print(auth_challenge)

	data1 = bytes.fromhex('011bed010000343000000000000041444d494e00000000005b41159d0000000000000000010000000200000000000000c98c9205d6cd9c0978507ee2fce00702b035a21b9e020000789c75d24d4ec4300c05e0700a36dc84159d91aa8ac98666d6c84d1eadd5c4a9d274feeec17d113b90dcf5673d5b4f7e36c634911f0f2ae1f3cd4f8c0b12a49e3bf394ae2f27f3cf0b8474d97ce52caa3554069475cacb0ed71af1c588c1b270a2451b62092ca31a70a008095434ca69a07acae3ae39dcaa82470cdbe8728eab826dbc2f937a4a6b0f13e9ddb5b6dfca05771d378ea1219955ed645de0f5d8ae22f5d9cfa87bf558f225abf2411c5470bf8deafb1c2758121aa1f5edf20cfd095ca1807ee618f79805e5afbd7e1fdf7f00e127c88d')
	auth_session = world.net.packets.CMSG_AUTH_SESSION.parse(data1)
	print(auth_session)

	assert auth_session.build == 12340
	assert auth_session.login_server_id == 0
	assert auth_session.account_name == 'ADMIN'
	assert auth_session.login_server_type == 0
	assert auth_session.region_id == 0
	assert auth_session.battlegroup_id == 0
	assert auth_session.realm_id == 1
	assert len(data1) == auth_session.header.size + 2

	data2 = bytes.fromhex('012fed010000343000000000000041444d494e00000000008a58920b0000000000000000010000000200000000000000b37231a713f7ace4197c3d14e3f1f095ded6683e9e020000789c75d2414ec33010055077c11958949bb022a91445d49bc6acab893d24a3d8e368e294b6f7e0089c8bab209040200debaf37df1ecdad31a68a74bd8284e3831f094f9890cb536b36e9e56e6ffee4820c7ab2fa4299bfb3edfbcddb4f5681f428cb98679556504ac467c2182c312598b519c481785007d410910388c2ea9c7a28fb3c68ec2b73782e0adc61bf0e2ee7b828b2b1f50845fd6b63bb554e78511fdac4cb3cea6ca5182ae049752d2f337abdb02d98baec272cffadc78297acda03505089fbdca8dee728a105860145837942fd089c40c06ea218f546016294dff4fe75f7f8015c7eda99')
	auth_session3 = world.net.packets.CMSG_AUTH_SESSION.parse(data2)
	print(f'good packet: {auth_session3}')
	print(len(data2))
	assert len(data2) == auth_session3.header.size + 2

	data3 = bytes.fromhex('012fed010000343000000000000041444d494e0000000000cd182e5400000000000000000100000001000000000000003d21ef05c54be91dc684aeab15b93a8b79e61e609e020000789c75d2414ec33010055077c11958949bb022a91445d49bc6acab893d24a3d8e368e294b6f7e0089c8bab209040200debaf37df1ecdad31a68a74bd8284e3831f094f9890cb536b36e9e56e6ffee4820c7ab2fa4299bfb3edfbcddb4f5681f428cb98679556504ac467c2182c312598b519c481785007d410910388c2ea9c7a28fb3c68ec2b73782e0adc61bf0e2ee7b828b2b1f50845fd6b63bb554e78511fdac4cb3cea6ca5182ae049752d2f337abdb02d98baec272cffadc78297acda03505089fbdca8dee728a105860145837942fd089c40c06ea218f546016294dff4fe75f7f8015c7eda99')
	print(world.net.packets.CMSG_AUTH_SESSION.parse(data3))

def test_world_auth_packets2():
	client_data = bytes.fromhex('012fed010000343000000000000041444d494e0000000000f32ebd3f000000000000000001000000000000000000000012516f1d035e11da1dbb2b69faa6cfd86a3b4e109e020000789c75d2414ec33010055077c11958949bb022a91445d49bc6acab893d24a3d8e368e294b6f7e0089c8bab209040200debaf37df1ecdad31a68a74bd8284e3831f094f9890cb536b36e9e56e6ffee4820c7ab2fa4299bfb3edfbcddb4f5681f428cb98679556504ac467c2182c312598b519c481785007d410910388c2ea9c7a28fb3c68ec2b73782e0adc61bf0e2ee7b828b2b1f50845fd6b63bb554e78511fdac4cb3cea6ca5182ae049752d2f337abdb02d98baec272cffadc78297acda03505089fbdca8dee728a105860145837942fd089c40c06ea218f546016294dff4fe75f7f8015c7eda99')
	client_auth_session = world.net.packets.CMSG_AUTH_SESSION.parse(client_data)
	print(f'{client_auth_session}')
	assert len(client_data) == client_auth_session.header.size + 2

	# assert client_auth_session

	client_seed = random.randint(0, 10000000)
	session_args = {
		'header': {'size': 61 + 237 + len('Garygarygary')},
		'account_name': 'GarygaryGary',
		'client_seed': client_seed,
		'account_hash': 0,
	}

	pont_packet = world.net.packets.CMSG_AUTH_SESSION.build(session_args)
	pont_session = world.net.packets.CMSG_AUTH_SESSION.parse(pont_packet)
	assert len(pont_packet) == pont_session.header.size + 2
	assert pont_session.client_seed == client_seed
	assert pont_session.account_name == 'GARYGARYGARY'

def test_unk():
	packet = b'\x8duyZ(5\x08C\xf0[\x19L\xfa\xacS5s\x96wT\xc1\x08\x16\x86_\x98Cm\xc9W7\x1fSzJ\xdb5A>\xb3\xb8'

	try:
		header = world.net.packets.parser.parse_header(packet)
		print(f'[_packet_dispatcher] header: {header=}')
	except:
		pass