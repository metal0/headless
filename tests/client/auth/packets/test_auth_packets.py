from pont_client.client import auth

def test_challenge_request_decode_encode():
	data = bytes.fromhex('00082300576f57000303053430363878006e69570053556e65d4feffff0ab3cd730541444d494e')
	challenge_request = auth.packets.ChallengeRequest.parse(data)
	print(challenge_request)
	print(auth.packets.ChallengeRequest.build(challenge_request))
	assert challenge_request.opcode == auth.packets.constants.Opcode.login_challenge
	assert challenge_request.response == auth.packets.constants.Response.db_busy
	assert challenge_request.game == 'WoW'
	assert challenge_request.version == [3, 3, 5]
	assert challenge_request.build == 12340
	assert challenge_request.architecture == 'x86'
	assert challenge_request.os == 'Win'
	assert challenge_request.ip == '10.179.205.115'
	assert challenge_request.country == 'enUS'
	assert challenge_request.timezone_bias == -300
	assert challenge_request.account_name == 'ADMIN'
	assert auth.packets.ChallengeRequest.build(challenge_request) == data
