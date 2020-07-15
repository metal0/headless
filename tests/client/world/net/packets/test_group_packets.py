from pont.client import world

async def test_group_invite():
	data = b'\x00\x10o\x00\x01Act\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	packet = world.net.packets.SMSG_GROUP_INVITE.parse(data)
	print(packet)

	assert packet.header.opcode == world.net.Opcode.SMSG_GROUP_INVITE
	assert packet.in_group == True
	assert packet.inviter == 'Act'
