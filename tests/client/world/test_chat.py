import trio
from pont.client.world.chat import ChatMessage
from pont.client.world.net import WorldClientProtocol
from tests.mock.world import MockWorld

# async def test_chat():
# 	client, server = trio.testing.memory_stream_pair()
# 	protocol = WorldClientProtocol(client, session_key=7)
# 	world = MockWorld(protocol, None)
# 	await ChatMessage.load_message(world,
