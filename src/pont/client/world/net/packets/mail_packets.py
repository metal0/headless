import construct
from enum import Enum

from pont.client.world.guid import Guid
from pont.client.world.net.opcode import Opcode
from pont.client.world.net.packets.headers import ServerHeader, ClientHeader
from pont.utility.construct import GuidConstruct, PackEnum

class MailType(Enum):
	normal = 0
	auction = 2
	creature = 3
	gameobject = 4
	calendar = 5

CMSG_GET_MAIL_LIST = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GET_MAIL_LIST, 8),
	'mailbox' / GuidConstruct(Guid),
)

# CMSG_SEND_MAIL = construct.Struct(
# 	'header' / ClientHeader(Opcode.CMSG_SEND_MAIL, ),
# 	''
# )

MailEnchantmentInfo = construct.Struct(
	'charges' / construct.Int32ul,
	'duration' / construct.Int32ul,
	'id' / construct.Int32ul
)

MailItemData = construct.Struct(
	'index' / construct.Byte,
	'guid_low' / construct.Int32ul,
	'entry' / construct.Int32ul,
	'enchantment' / construct.Array(7, MailEnchantmentInfo),
	'property_id' / construct.Int32ul,
	'suffix_factor' / construct.Int32ul,
	'count' / construct.Int32ul,
	'charges' / construct.Int32ul,
	'max_durability' / construct.Int32ul,
	'durability' / construct.Int32ul,
	construct.Padding(1)
)

MailMessageData = construct.Struct(
	'size' / construct.Int16ul,
	'id' / construct.Int32ul,
	'type' / PackEnum(MailType),
	'sender' / construct.Switch(
		construct.this.type, {
			MailType.normal: GuidConstruct(Guid),
			MailType.creature: construct.Int32ul,
			MailType.gameobject: construct.Int32ul,
			MailType.auction: construct.Int32ul,
			MailType.calendar: construct.Int32ul,
		}
	),

	'cod' / construct.Int32ul,
	construct.Padding(4),
	'stationery' / construct.Int32ul,
	'money' / construct.Int32ul,
	'checked' / construct.Int32ul,
	'timestamp'  / construct.Float32l,
	'mail_template' / construct.Int32ul,
	'subject' / construct.CString('utf8'),
	'body' / construct.CString('utf8'),
	'sent_items' / construct.PrefixedArray(construct.Byte, MailItemData)
)

SMSG_MAIL_LIST_RESULT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_MAIL_LIST_RESULT),
	'total_num_mail' / construct.Int32ul,
	'mail' / construct.PrefixedArray(construct.Byte, MailMessageData)
)