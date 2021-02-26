from pont.client.world import Guid
from pont.client.world.net.packets import CMSG_AUCTION_LIST_OWNER_ITEMS, CMSG_AUCTION_LIST_PENDING_SALES
from pont.client.world.net.packets.auction_packets import SMSG_AUCTION_LIST_RESULT, CMSG_AUCTION_LIST_ITEMS

async def test_SMSG_AUCTION_LIST_RESULT():
	data = b'\x00\x0e\\\x02\x00\x00\x00\x00\x00\x00\x00\x00,\x01\x00\x00'
	packet = SMSG_AUCTION_LIST_RESULT.parse(data)
	print(packet)

	assert packet.count == 0
	assert packet.total_count == 0
	assert packet.cooldown == 300
	assert len(packet.auctions) == 0

async def test_CMSG_AUCTION_LIST_OWNER_ITEMS():
	# packet=Container(header=Container(size=0, opcode=<Opcode.CMSG_AUCTION_LIST_OWNER_ITEMS: 601>), auctioneer=9009462722924549, list_start=1052464)
	data = b'\x00\x00Y\x02\x00\x00\x05\x907\x01\x0f\x02 \x000\x0f\x10\x00'
	packet = CMSG_AUCTION_LIST_OWNER_ITEMS.parse(data)
	print(packet)

	assert packet.auctioneer == Guid(value=0x20020f01379005)
	assert packet.list_start == 1052464


async def test_CMSG_AUCTION_LIST_PENDING_SALES():
	# header=Container(size=0,opcode= <Opcode.CMSG_AUCTION_LIST_PENDING_SALES: 1167>), auctioneer = 9009462722924549)
	data = b'\x00\x00\x8f\x04\x00\x00\x05\x907\x01\x0f\x02 \x00'
	packet = CMSG_AUCTION_LIST_PENDING_SALES.parse(data)
	print(packet)

async def test_CMSG_AUCTION_LIST_ITEMS():
	# data = byte(88), byte(2), byte(0), byte(0), byte(90), byte(55), byte(1), byte(222), byte(33), byte(0), byte(48), byte(241), byte(0), byte(0), byte(0), byte(0), byte(98), byte(114), byte(101), byte(97), byte(100), byte(0), byte(0), byte(0), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(255), byte(0), byte(0), byte(7), byte(1), byte(0), byte(0), byte(1), byte(5), byte(0), byte(6), byte(0), byte(9), byte(1), byte(8), byte(0), byte(3), byte(0)
	data = b'\x00+X\x02\x00\x00Z7\x01\xde!\x000\xf1\x00\x00\x00\x00Bread\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00'
	packet = CMSG_AUCTION_LIST_ITEMS.parse(data)
	print(packet)