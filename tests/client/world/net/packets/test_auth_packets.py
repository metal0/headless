import random

from pont.client import world
from pont.client.world.expansion import Expansion
from pont.client.world.net import Opcode
from pont.client.world.net.packets.auth_packets import AuthResponse

def test_world_auth_packet():
	data = bytes.fromhex('002aec01010000004c6f82e4ab892d3d480a9898d510f879f862479fad62c8815ff00fd85e5ab6b4031684e9')
	auth_challenge = world.net.packets.SMSG_AUTH_CHALLENGE.parse(data)
	assert auth_challenge.header.size == len(data) - 2
	assert auth_challenge.server_seed == 3833753420
	assert auth_challenge.encryption_seed1 == 211717911769230637244251202614564063659
	assert auth_challenge.encryption_seed2 == 310395952709835516542653712987794727597
	print(auth_challenge)

	data0 = bytes.fromhex('010000008ECC9FDBCD1F27CEABF0E9AA76AB9A09BEC6DDB30191D5023A19737F2C41F060128CC796')
	auth_challenge = world.net.packets.SMSG_AUTH_CHALLENGE.parse(data)
	# assert auth_challenge.header.size + 2 == len(data0)
	assert auth_challenge.server_seed == 3833753420
	assert auth_challenge.encryption_seed1 == 211717911769230637244251202614564063659
	assert auth_challenge.encryption_seed2 == 310395952709835516542653712987794727597
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
	data = b'\x01\x19\xed\x01\x00\x0040\x00\x00\x00\x00\x00\x00ADMIN\x00\x00\x00\x00\x00\x1e\xe2\x86\x85\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\xe7\xb4\x8a\x7fG\xd4\xc1/\xf0t\xd0\xb1\xdc#\x1f!\x1bO\xad\x82\x9e\x02\x00\x00x\x9cu\xd2\xc1j\xc30\x0c\xc6q\xef)v\xe9\x9b\xec\xb4\xb4P\xc2\xea\xcb\xe2\x9e\x8bb\x7fKDl98N\xb7\xf6=\xfa\xbee\xb7\r\x94\xf3OH\xf0G\xaf\xc6\x98&\xf2\xfdN%\\\xde\xfd\xc8\xb8"A\xea\xb95/\xe9{w2\xff\xbc@H\x97\xd5W\xce\xa2ZC\xa5GY\xc6<op\xad\x11_\x8c\x18,\x0b\'\x9a\xb5!\x96\xc02\xa8\x0b\xf6\x14!\x81\x8aF9\xf5TOy\xd84\x87\x9f\xaa\xe0\x01\xfd:\xb8\x9c\xe3\xa2\xe0\xd1\xeeG\xd2\x0b\x1dm\xb7\x96+n:\xc6\xdb<\xea\xb2r\x0c\r\xc9\xa4j+\xcb\x0c\xaf\x1fl+R\x97\xfd\x84\xba\x95\xc7\x92/Y\x95O\xe2\xa0\x82\xfb-\xaa\xdfs\x9c`Ih\x80\xd6\xdb\xe5\t\xfa\x13\xb8B\x01\xdd\xc41n1\x0b\xca_{{\x1c>\x9e\xe1\x93\xc8\x8d'
	print(f'{world.net.packets.CMSG_AUTH_SESSION.parse(data)=}')

	client_data = bytes.fromhex('012fed010000343000000000000041444d494e0000000000f32ebd3f000000000000000001000000000000000000000012516f1d035e11da1dbb2b69faa6cfd86a3b4e109e020000789c75d2414ec33010055077c11958949bb022a91445d49bc6acab893d24a3d8e368e294b6f7e0089c8bab209040200debaf37df1ecdad31a68a74bd8284e3831f094f9890cb536b36e9e56e6ffee4820c7ab2fa4299bfb3edfbcddb4f5681f428cb98679556504ac467c2182c312598b519c481785007d410910388c2ea9c7a28fb3c68ec2b73782e0adc61bf0e2ee7b828b2b1f50845fd6b63bb554e78511fdac4cb3cea6ca5182ae049752d2f337abdb02d98baec272cffadc78297acda03505089fbdca8dee728a105860145837942fd089c40c06ea218f546016294dff4fe75f7f8015c7eda99')
	client_auth_session = world.net.packets.CMSG_AUTH_SESSION.parse(client_data)
	print(f'{client_auth_session}')
	assert len(client_data) == client_auth_session.header.size + 2

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

def test_auth_response():
	data = bytes.fromhex('000DEE010C00000000000000000002')
	packet = world.net.packets.SMSG_AUTH_RESPONSE.parse(data)
	assert packet.header.size == len(data) - 2
	assert packet.header.opcode == Opcode.SMSG_AUTH_RESPONSE
	assert packet.response == AuthResponse.ok
	assert packet.billing_time_remaining == 0
	assert packet.billing_plan_flags == 0
	assert packet.billing_time_rested == 0
	assert packet.expansion == Expansion.wotlk
	assert packet.queue_position is None

def test_unk():
	packet = b'\x8duyZ(5\x08C\xf0[\x19L\xfa\xacS5s\x96wT\xc1\x08\x16\x86_\x98Cm\xc9W7\x1fSzJ\xdb5A>\xb3\xb8'

	try:
		header = world.net.packets.parser.parse_header(packet)
		print(f'[_packet_dispatcher] header: {header=}')
	except:
		pass