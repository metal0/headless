from pont.client.world import Guid
from pont.client.world.chat.message import MessageType
from pont.client.world.language import Language
from pont.client.world.net import packets, Opcode

async def test_CMSG_MESSAGECHAT():
	# data = b''
	# packet = packets.CMSG_MESSAGECHAT.parse(data)
	# print(packet)
	pass

async def test_SMSG_MESSAGECHAT():
	data = b'\x003\x96\x00\x0c\x00\x00\x00\x00k7\x01\xbe\r\x000\xf1\x00\x00\x00\x00\x0e\x00\x00\x00Thomas Miller\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00'
	packet = packets.SMSG_MESSAGECHAT.parse(data)
	print(packet)

	assert packet.header.opcode == Opcode.SMSG_MESSAGECHAT
	assert packet.header.size == 51

	assert packet.message_type == MessageType.monster_say
	assert packet.language == Language.universal
	assert packet.sender_guid == Guid(value=0xf130000dbe01376b)
	assert packet.flags == 0
	assert packet.info.sender == 'Thomas Miller'
	assert packet.info.receiver_guid == Guid()
	assert packet.info.receiver is None
	assert packet.text == ''
	assert packet.chat_tag == 0
	assert packet.achievement_id is None

	data2 = b'\x00#\x96\x00\x01\x07\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00ay\x00\x04'
	packet2 = packets.SMSG_MESSAGECHAT.parse(data2)
	print(data2)

	assert packet2.header.opcode == Opcode.SMSG_MESSAGECHAT
	assert packet2.header.size == 35

	assert packet2.message_type == MessageType.say
	assert packet2.language == Language.common
	assert packet2.sender_guid == Guid(1)
	assert packet2.flags == 0
	assert packet2.info.receiver_guid == Guid(1)
	assert packet2.text == 'ay'
	assert packet2.chat_tag == 4
	assert packet2.achievement_id is None

	data3 = b'\x00%\x96\x00\x07\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00ayte\x00\x04'
	packet3 = packets.SMSG_MESSAGECHAT.parse(data3)
	print(packet3)

	assert packet3.header.opcode == Opcode.SMSG_MESSAGECHAT
	assert packet3.header.size == 37

	assert packet3.message_type == MessageType.whisper
	assert packet3.language == Language.universal
	assert packet3.sender_guid == Guid(1)
	assert packet3.flags == 0
	assert packet3.info.receiver_guid == Guid(1)
	assert packet3.text == 'ayte'
	assert packet3.chat_tag == 4
	assert packet3.achievement_id is None

	data4 = b"\x00A\x96\x00\x04\xff\xff\xff\xff\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\x00\x00\x00Crb\tS% fa692e 7b5D}'$s'7*Wisplol\x00\x00"
	packet4 = packets.SMSG_MESSAGECHAT.parse(data4)
	print(packet4)

	assert packet4.header.size == 65
	assert packet4.header.opcode == Opcode.SMSG_MESSAGECHAT

	assert packet4.message_type == MessageType.guild
	assert packet4.language == Language.addon
	assert packet4.sender_guid == Guid(0x15)
	assert packet4.flags == 0
	assert packet4.info.receiver_guid == Guid()
	assert packet4.text == 'Crb\tS% fa692e 7b5D}\'$s\'7*Wisplol'
	assert packet4.chat_tag == 0
	assert packet4.achievement_id is None

async def test_SMSG_GM_MESSAGECHAT():
	data =b'\x006\xb3\x03\x02\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00Act\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x00DBMv4-Ver\tHi!\x00\x04'
	packet = packets.SMSG_GM_MESSAGECHAT.parse(data)
	print(packet)

	assert packet.header.opcode == Opcode.SMSG_GM_MESSAGECHAT
	assert packet.header.size == 54

	assert packet.message_type == MessageType.party
	assert packet.language == Language.addon
	assert packet.sender_guid == Guid(1)
	assert packet.flags == 0
	assert packet.info.sender == 'Act'
	assert packet.info.receiver_guid == Guid()
	assert packet.text == 'DBMv4-Ver\tHi!'
	assert packet.chat_tag == 4
	assert packet.achievement_id is None

	data2 = b'\x01(\xb3\x03\x04\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00Act\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor i\x00\x04'
	packet2 = packets.SMSG_GM_MESSAGECHAT.parse(data2)
	print(packet2)

	assert packet2.header.opcode == Opcode.SMSG_GM_MESSAGECHAT
	assert packet2.header.size == 296

	assert packet2.message_type == MessageType.guild
	assert packet2.language == Language.universal
	assert packet2.sender_guid == Guid(1)
	assert packet2.flags == 0
	assert packet2.info.sender == 'Act'
	assert packet2.info.receiver_guid == Guid()
	assert packet2.text == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor i'
	assert packet2.chat_tag == 4
	assert packet2.achievement_id is None