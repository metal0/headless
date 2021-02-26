import time

import pont
from pont.client.auth.net import packets
from pont.client.auth.net.packets import ResponseHeader
from pont.utility.string import bytes_to_int

def test_challenge_request_packet1():
	packet = bytes.fromhex('00082300576f57000303053430363878006e69570053556e65d4feffff0ab3cd730541444d494e')
	challenge_request = packets.ChallengeRequest.parse(packet)

	assert challenge_request.header.opcode == pont.client.auth.net.Opcode.login_challenge
	assert challenge_request.header.response == pont.client.auth.net.Response.db_busy
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

	assert challenge_request.header.opcode == pont.client.auth.net.Opcode.login_challenge
	assert challenge_request.header.response == pont.client.auth.net.Response.success
	assert challenge_request.game == 'WoW'
	assert challenge_request.version == '3.3.5'
	assert challenge_request.build == 12340
	assert challenge_request.architecture == 'x86'
	assert challenge_request.os == 'Win'
	assert challenge_request.country == 'enUS'
	assert challenge_request.timezone_bias == -300
	assert challenge_request.account_name == 'LONGMANYES'
	assert packets.ChallengeRequest.build(challenge_request) == packet

	szn_data = b"\x00\x08&\x00WoW\x00\x03\x03\x054068x\x00XSO\x00SUne\xd4\xfe\xff\xff\xa0'\x84\\\x08CHEESEMO"
	szn_challenge = packets.ChallengeRequest.parse(szn_data)
	print(szn_challenge)

	warmane_bug_data = b"\x00\x08'\x00WoW\x00\x03\x03\x054068x\x00XSO\x00SUne\xd4\xfe\xff\xffh\xfe\tp\tFLOWERMOM"
	print(packets.ChallengeRequest.parse(warmane_bug_data))
	# print(szn_challenge)

def test_challenge_request_named_args():
	packet = packets.ChallengeRequest.build({
		'game': 'WoW',
		'os': 'Win',
		'country': 'enUS',
		'account_name': 'ADMIN'
	})


def test_challenge_response_packet1():
	packet = bytes.fromhex('0000006f168b46a9cd26b0adb481c59d92ba2f8e5432918abb90f0805677cc085d6a07010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89fb348ce3fd604ea01f910e12b900588375197e0172df0ae9df5fac2e22227ea6c5a970407fe7d52276c97e13e71695d300')
	challenge_response = packets.ChallengeResponse.parse(packet)
	assert challenge_response.header.response == pont.client.auth.net.Response.success
	assert challenge_response.server_public == 3354117828571998584191894319144934700250845415608995089404241538219888023151
	assert challenge_response.generator_length == 1
	assert challenge_response.generator == 7
	assert challenge_response.prime_length == 32
	assert challenge_response.prime == 62100066509156017342069496140902949863249758336000796928566441170293728648119
	assert challenge_response.salt == 75306791175913550635130350707151637678476193135459206924908206791041802319099
	assert packets.ChallengeResponse.build(challenge_response) == packet

	szn_data = bytes.fromhex('000000675f54d1e65a382bc343730cac11dcaa4c0204a1a45a3e87c4b31bed6933eb55010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b8979604517f018fa18b3b99bb764cbcb33bed1e3db2ccc17bac1a2cb062e86cdd40166742b495c252c46876a1a3e7d18e200')
	print(packets.ChallengeResponse.parse(szn_data))

	warmane_bug_data = bytes.fromhex('000000153ce50a2a341987445c88a85e650599a684a84b7f43c5c57921bd183f1db105010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89ed5be899b7acc1a3514d8c93d997329fd6756f744b1be29c0a51a2c995b7cae5baa31e99a00b2157fc373fb369cdd2f100')
	print(packets.ChallengeResponse.parse(warmane_bug_data))


def test_challenge_response_packet2():
	packet = bytes.fromhex('0000009ef68afffcd1328866b564d4bb0b12249a8df90e07bcd6064845ab64b482e11c010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89319782ba4be5e9fc8e11cf9d7261f450ee7344aee4e402f6a3d0319c7ac425eabaa31e99a00b2157fc373fb369cdd2f100')

	challenge_response = packets.ChallengeResponse.parse(packet)
	assert challenge_response.header.opcode == pont.client.auth.net.Opcode.login_challenge
	assert challenge_response.header.response == pont.client.auth.net.Response.success
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
		'checksum': 0,
		'security_flag': 0,
	})

	challenge_response = packets.ChallengeResponse.parse(packet)
	assert challenge_response.header.opcode == pont.client.auth.net.Opcode.login_challenge
	assert challenge_response.header.response == pont.client.auth.net.Response.success
	assert challenge_response.server_public == 37573892888418226681312157480058717812018111076215085243857638337566340538151
	assert challenge_response.generator_length == 1
	assert challenge_response.generator == 7
	assert challenge_response.prime_length == 32
	assert challenge_response.prime == 62100066509156017342069496140902949863249758336000796928566441170293728648119
	assert challenge_response.salt == 105907935957727809645867901940389592363084317324947500788246621423699503519537

	assert pont.client.auth.net.packets.ChallengeResponse.build(challenge_response) == packet

def test_proof_request_packet1():
	packet = bytes.fromhex('01aab3826c0963de7881f5741733d7b8c2fb98b6f14bf33a790e6d376793895a06f122681f01b74c8b4100f5856fbcc03d80da65f378f6fd38b5843abf6884d7ca207b4187b84ec6d10000')
	proof_request = pont.client.auth.net.packets.ProofRequest.parse(packet)

	assert proof_request.opcode == pont.client.auth.net.Opcode.login_proof
	assert proof_request.client_public == bytes_to_int(packet[1:33])
	assert proof_request.session_proof == bytes_to_int(packet[33:53])
	assert proof_request.checksum == bytes_to_int(packet[53:73])
	assert proof_request.num_keys == 0

	assert proof_request.security_flags == 0
	assert pont.client.auth.net.packets.ProofRequest.build(proof_request) == packet

	szn_data = bytes.fromhex('01c37ba092fdd5896322660a26247140e03691b2a3176228bc907a3809340bf124734b27330d66a2b2a63c79418743b139de9e1ef6deb96d9392a937bef78f0c38ed8754edcf53ce000000')
	print(packets.ProofRequest.parse(szn_data))

	warmane_bug_data = bytes.fromhex('018d8c4bd5e7985bea278ef2984544550992fe45364e7b96cc0af9b34c76ca121bb9ed4eb5945c14c0fe51fcb57fe0698da321795adeb96d9392a937bef78f0c38ed8754edcf53ce000000')
	print(packets.ProofRequest.parse(szn_data))

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
	assert proof_response.header.opcode == pont.client.auth.net.Opcode.login_proof
	assert proof_response.header.response == pont.client.auth.net.Response.success
	assert proof_response.session_proof_hash == bytes_to_int(packet[2:22])
	assert proof_response.account_flags == 32768
	assert proof_response.survey_id == 0
	assert proof_response.login_flags == 0

	assert packets.ProofResponse.build(proof_response) == packet

def test_proof_response_packet2():
	packet = packets.ProofResponse.build(dict(session_proof_hash=1460130100480076755268286359902044858927415901776))

	proof_response = packets.ProofResponse.parse(packet)
	print(f'{proof_response=}')
	assert proof_response.session_proof_hash == 1460130100480076755268286359902044858927415901776
	assert proof_response.header.opcode == pont.client.auth.net.Opcode.login_proof
	assert proof_response.header.response == pont.client.auth.net.Response.success
	assert proof_response.login_flags == 0
	assert proof_response.survey_id == 0
	assert proof_response.account_flags == 32768
	assert packets.ProofResponse.build(proof_response) == packet
