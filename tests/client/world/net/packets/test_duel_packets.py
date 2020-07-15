from pont.client import world

def test_SMSG_DUEL_REQUESTED():
	data = b'\x00\x12g\x01`\xf1 \xb0T\x00\x10\xf1\x01\x00\x00\x00\x00\x00\x00\x00'
	packet = world.net.packets.SMSG_DUEL_REQUESTED.parse(data)
	print(packet)