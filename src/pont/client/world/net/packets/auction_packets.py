import construct

from pont.client.world.guid import Guid
from pont.client.world.net.opcode import Opcode
from pont.client.world.net.packets.headers import ServerHeader, ClientHeader
from pont.utility.construct import GuidConstruct

SMSG_AUCTION_HELLO = construct.Struct(
	'header' / ServerHeader(Opcode.MSG_AUCTION_HELLO),
	'auctioneer' / GuidConstruct(Guid),
	'house_id' / construct.Default(construct.Int32ul, 1),
	'is_ah_enabled' / construct.Default(construct.Flag, True)
)

CMSG_AUCTION_HELLO = construct.Struct(
	'header' / ClientHeader(Opcode.MSG_AUCTION_HELLO),
	'auctioneer' / GuidConstruct(Guid),
)

def MSG_AUCTION_HELLO(server=False):
	return SMSG_AUCTION_HELLO if server else CMSG_AUCTION_HELLO

SMSG_AUCTION_COMMAND_RESULT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUCTION_COMMAND_RESULT, 4 + 4 + 4),
	'auction_id' / construct.Int32sl,
	'action' / construct.Int32sl,
	'error' / construct.Int32sl,
)

CMSG_AUCTION_SELL_ITEM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_SELL_ITEM),
	'auctioneer' / GuidConstruct(Guid),
	'items' / construct.PrefixedArray(construct.Int32ul, construct.Struct(
		'guid' / GuidConstruct(Guid),
		'count' / construct.Int32ul
	)),

	'bid' / construct.Int32ul,
	'buyout' / construct.Int32ul,
	'expiry_time' / construct.Int32ul,
)

CMSG_AUCTION_REMOVE_ITEM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_REMOVE_ITEM, 8 + 4),
	'auctioneer' / GuidConstruct(Guid),
	'auction_id' / construct.Int32sl,
)

CMSG_AUCTION_PLACE_BID = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_PLACE_BID, 8 + 4 + 4),
	'auctioneer' / GuidConstruct(Guid), # TODO: Check here or above packet
	'auction_id' / construct.Int32sl,
	'price' / construct.Int32sl,
)

# We might need to do some more work to explore this packet's structure but this might be okay for now.
CMSG_AUCTION_LIST_ITEMS = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_LIST_ITEMS),
	'auctioneer' / GuidConstruct(Guid),
	'list_start' / construct.Int32ul,
	'search_term' / construct.CString('utf8'),
	'min_level' / construct.Default(construct.Byte, 0),
	'max_level' / construct.Default(construct.Byte, 80),
	'slot_id' / construct.Default(construct.Int32ul, 0),
	'category' / construct.Default(construct.Int32ul, 0),
	'subcategory' / construct.Default(construct.Int32ul, 0),
	'rarity' / construct.Default(construct.Int32ul, 0),
	'usable' / construct.Default(construct.Flag, False),
	'is_full' / construct.Default(construct.Flag, True),
	construct.Padding(1)
	# construct.PrefixedArray(construct.Default(construct.Byte, 0), construct.Padding(2)),
)

# Based on the following:
# vType));           // usable
#     CDataStore::PutInt8(v7 != 0);                   // full query?
#     LOBYTE(itemClass) = 0;
#     itemSubClass2 = data.m_size;
#     CDataStore::PutInt8(0);                         // placeholder
#     v10 = 0;
#     v11 = g_auctionSort;
#     HIDWORD(invType) = 12;
#     do
#     {
#         if ( v10 < 12 && v11 && v11->isSorted )
#         {
#             CDataStore::PutInt8(v11->sortColumn);
#             CDataStore::PutInt8(v11->Reversed != 0);
#             LOBYTE(itemClass) = itemClass + 1;
#         }
#         ++v10;
#         ++v11;
#         --HIDWORD(invType);
#     }
#     while ( HIDWORD(invType) );
#     CDataStore::PutInt8AtPos(&data, itemSubClass2, itemClass);
#     data.m_read = 0;
#     ClientServices::SendPacket_1(&data);

AuctionEnchantmentInfo = construct.Struct(
	'charges' / construct.Int32ul,
	'duration' / construct.Int32ul,
	'id' / construct.Int32ul
)

AuctionInfo = construct.Struct(
	'id' / construct.Int32ul,
	'entry_id' / construct.Int32ul,
	'enchantments' / construct.Array(7, AuctionEnchantmentInfo),
	'random_property_id' / construct.Int32ul,
	'suffix_factor' / construct.Int32ul,
	'num_items' / construct.Int32ul,
	'spell_charges' / construct.Int32ul,
	construct.Padding(4),
	'owner' / GuidConstruct(Guid),
	'start_bid' / construct.Int32ul,
	'buyout' / construct.Int32ul,
	'time_left' / construct.Int32ul,
	'bidder' / GuidConstruct(Guid),
	'bid' / construct.Int32ul
)

SMSG_AUCTION_LIST_RESULT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUCTION_LIST_RESULT, 4 + 4 + 4),
	'count' / construct.Int32ul,
	'total_count' / construct.Int32ul,
	'cooldown' / construct.Int32ul,
	'auctions' / construct.Array(construct.this.count, AuctionInfo),
)

CMSG_AUCTION_LIST_OWNER_ITEMS = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_LIST_OWNER_ITEMS, 8 + 4),
	'auctioneer' / GuidConstruct(Guid),
	'list_start' / construct.Int32ul,
)

CMSG_AUCTION_LIST_PENDING_SALES = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUCTION_LIST_PENDING_SALES, 8),
	'auctioneer' / GuidConstruct(Guid),
)

PendingSale = construct.Struct(
	'info1' / construct.CString('utf8'),
	'info2' / construct.CString('utf8'),
	construct.Padding(8 + 4),
	'time_left' / construct.Float32l
)

SMSG_AUCTION_LIST_PENDING_SALES = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUCTION_LIST_PENDING_SALES, 8),
	'sales' / construct.PrefixedArray(construct.Int32ul, PendingSale)
)