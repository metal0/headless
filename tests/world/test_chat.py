import trio
from wlink.world import WorldClientProtocol
from wlink.world.packets import SMSG_MESSAGECHAT, Language
from tests.mock.world import MockWorld

async def test_chat():
	client, server = trio.testing.memory_stream_pair()
	protocol = WorldClientProtocol(client, session_key=7)
	# world = MockWorld(protocol, None, emitter=None)

	data = b'\x00*\x96\x00\x04\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00HealBot\tG\x00\x00'
	packet = SMSG_MESSAGECHAT.parse(data)

	assert packet.text == 'HealBot\tG'
	assert packet.chat_tag == 0
	assert packet.language == Language.addon

