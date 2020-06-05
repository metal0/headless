import time

from pont_client.client import auth
from pont_client.client.auth.net import packets
from pont_client.utility.string import bytes_to_int

def test_challenge_request_packet1():
	packet = bytes.fromhex('00082300576f57000303053430363878006e69570053556e65d4feffff0ab3cd730541444d494e')
	challenge_request = packets.ChallengeRequest.parse(packet)

	assert challenge_request.opcode == packets.constants.Opcode.login_challenge
	assert challenge_request.response == packets.constants.Response.db_busy
	assert challenge_request.game == 'WoW'
	assert challenge_request.version == '3.3.5'
	assert challenge_request.build == 12340
	assert challenge_request.architecture == 'x86'
	assert challenge_request.os == 'Win'
	assert str(challenge_request.ip) == '10.179.205.115'
	assert challenge_request.country == 'enUS'
	assert challenge_request.timezone_bias == -300
	assert challenge_request.account_name == 'ADMIN'
	assert packets.ChallengeRequest.build(challenge_request) == packet


def test_challenge_request_packet2():
	packet = bytes.fromhex('00002800576f57000303053430363878006e69570053556e65d4feffff000000000a4c4f4e474d414e594553')
	challenge_request = packets.ChallengeRequest.parse(packet)

	assert challenge_request.opcode == packets.constants.Opcode.login_challenge
	assert challenge_request.response == packets.constants.Response.success
	assert challenge_request.game == 'WoW'
	assert challenge_request.version == '3.3.5'
	assert challenge_request.build == 12340
	assert challenge_request.architecture == 'x86'
	assert challenge_request.os == 'Win'
	assert challenge_request.country == 'enUS'
	assert challenge_request.timezone_bias == -300
	assert challenge_request.account_name == 'LONGMANYES'
	assert packets.ChallengeRequest.build(challenge_request) == packet

def test_challenge_request_named_args():
	packet = packets.ChallengeRequest.build({
		'game': 'WoW',
		'os': 'Win',
		'country': 'enUS',
		'account_name': 'ADMIN'
	})

	challenge_request = packets.ChallengeRequest.parse(packet)
	assert challenge_request.opcode == packets.constants.Opcode.login_challenge
	assert challenge_request.architecture == 'x86'
	assert challenge_request.country == 'enUS'
	assert challenge_request.account_name == 'ADMIN'
	assert challenge_request.timezone_bias == int(-time.timezone / 60)
	assert challenge_request.build == 12340
	assert challenge_request.ip == '127.0.0.1'
	assert challenge_request.packet_size == 34 + len(challenge_request.account_name)
	assert packets.ChallengeRequest.build(challenge_request) == packet

def test_challenge_response_packet1():
	packet = bytes.fromhex(
		'0000006f168b46a9cd26b0adb481c59d92ba2f8e5432918abb90f0805677cc085d6a07010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89fb348ce3fd604ea01f910e12b900588375197e0172df0ae9df5fac2e22227ea6c5a970407fe7d52276c97e13e71695d300')
	challenge_response = packets.ChallengeResponse.parse(packet)
	print(challenge_response)

	assert challenge_response.response == packets.constants.Response.success
	assert challenge_response.server_public == 3354117828571998584191894319144934700250845415608995089404241538219888023151
	assert challenge_response.generator_length == 1
	assert challenge_response.generator == 7
	assert challenge_response.prime_length == 32
	assert challenge_response.prime == 62100066509156017342069496140902949863249758336000796928566441170293728648119
	assert challenge_response.salt == 75306791175913550635130350707151637678476193135459206924908206791041802319099

	assert packets.ChallengeResponse.build(challenge_response) == packet

def test_challenge_response_packet2():
	packet = bytes.fromhex('0000009ef68afffcd1328866b564d4bb0b12249a8df90e07bcd6064845ab64b482e11c010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89319782ba4be5e9fc8e11cf9d7261f450ee7344aee4e402f6a3d0319c7ac425eabaa31e99a00b2157fc373fb369cdd2f100')

	challenge_response = packets.ChallengeResponse.parse(packet)
	assert challenge_response.opcode == packets.constants.Opcode.login_challenge
	assert challenge_response.response == packets.constants.Response.success
	assert challenge_response.server_public == int.from_bytes(packet[3:35], byteorder='little', signed=False)
	assert challenge_response.generator_length == 1
	assert challenge_response.generator == 7
	assert challenge_response.prime_length == 32
	assert challenge_response.prime == 62100066509156017342069496140902949863249758336000796928566441170293728648119
	assert challenge_response.salt == int.from_bytes(packet[70:102], 'little', signed=False)
	assert packets.ChallengeResponse.build(challenge_response) == packet

def test_challenge_response_named_args():
	packet = packets.ChallengeResponse.build({
		'server_public': 37573892888418226681312157480058717812018111076215085243857638337566340538151,
		'gen_len': 1,
		'generator': 7,
		'prime_len': 32,
		'prime': 62100066509156017342069496140902949863249758336000796928566441170293728648119,
		'salt': 105907935957727809645867901940389592363084317324947500788246621423699503519537,
		'checksum_salt': 0,
		'security_flag': 0,
	})

	challenge_response = packets.ChallengeResponse.parse(packet)
	assert challenge_response.opcode == packets.constants.Opcode.login_challenge
	assert challenge_response.response == packets.constants.Response.success
	assert challenge_response.server_public == 37573892888418226681312157480058717812018111076215085243857638337566340538151
	assert challenge_response.generator_length == 1
	assert challenge_response.generator == 7
	assert challenge_response.prime_length == 32
	assert challenge_response.prime == 62100066509156017342069496140902949863249758336000796928566441170293728648119
	assert challenge_response.salt == 105907935957727809645867901940389592363084317324947500788246621423699503519537

	assert auth.net.packets.ChallengeResponse.build(challenge_response) == packet

def test_proof_request_packet1():
	packet = bytes.fromhex('01aab3826c0963de7881f5741733d7b8c2fb98b6f14bf33a790e6d376793895a06f122681f01b74c8b4100f5856fbcc03d80da65f378f6fd38b5843abf6884d7ca207b4187b84ec6d10000')
	proof_request = auth.net.packets.ProofRequest.parse(packet)

	assert proof_request.opcode == packets.constants.Opcode.login_proof
	assert proof_request.client_public == bytes_to_int(packet[1:33])
	assert proof_request.session_proof == bytes_to_int(packet[33:53])
	assert proof_request.checksum == bytes_to_int(packet[53:73])
	assert proof_request.num_keys == 0

	assert proof_request.security_flags == 0
	assert auth.net.packets.ProofRequest.build(proof_request) == packet

def test_proof_request_packet2():
	packet = packets.ProofRequest.build({
		'client_public': 77210350023438834003517310668311813995313295286472098864964747603624128502278,
		'session_proof': 1376634071334066614958602446639008698865859323379,
		'checksum': 690586934523129401082830062357295166614403991249,
	})

	proof_request = packets.ProofRequest.parse(packet)
	assert proof_request.client_public == 77210350023438834003517310668311813995313295286472098864964747603624128502278
	assert proof_request.session_proof == 1376634071334066614958602446639008698865859323379
	assert proof_request.checksum == 690586934523129401082830062357295166614403991249

	assert packets.ProofRequest.build(proof_request) == packet

def test_proof_response_packet1():
	packet = bytes.fromhex('0100503e596c7ffe437f1d87506014552473877fc2ff00008000000000000000')
	proof_response = packets.ProofResponse.parse(packet)
	assert proof_response.opcode == packets.constants.Opcode.login_proof
	assert proof_response.response == packets.constants.Response.success
	assert proof_response.session_proof_hash == bytes_to_int(packet[2:22])
	assert proof_response.account_flags == 32768
	assert proof_response.survey_id == 0
	assert proof_response.login_flags == 0

	assert packets.ProofResponse.build(proof_response) == packet

def test_proof_response_packet2():
	packet = packets.ProofResponse.build({'session_proof_hash': 1460130100480076755268286359902044858927415901776})

	proof_response = packets.ProofResponse.parse(packet)
	assert proof_response.session_proof_hash == 1460130100480076755268286359902044858927415901776
	assert proof_response.opcode == packets.constants.Opcode.login_proof
	assert proof_response.response == packets.constants.Response.success
	assert proof_response.login_flags == 0
	assert proof_response.survey_id == 0
	assert proof_response.account_flags == 32768
	assert packets.ProofResponse.build(proof_response) == packet

def test_proof_response_error():
	data = bytes.fromhex('010400000000')
	# with pytest.raises(utility.StructParseError):
	# 	packet = pont.client.packets.ProofResponse(raw_bytes=data)
	# 	assert packet.opcode == auth.Opcode.login_proof
	# 	assert packet.error == auth.errors.unknown_account

