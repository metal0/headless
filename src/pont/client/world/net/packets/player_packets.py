import construct

from pont.client.world.items import ItemClass
from pont.client.world.net import Opcode
from pont.client.world.net.packets.headers import ServerHeader
from pont.utility.construct import PackEnum

SMSG_SET_PROFICIENCY = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_SET_PROFICIENCY, 1 + 4),
	'item_class' / PackEnum(ItemClass, construct.Byte),
	'item_subclass_mask' / construct.Int32ul
)