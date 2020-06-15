import construct

from pont_client.client.world.net.packets.constants import Opcode
from pont_client.utility.construct import PackEnum

Header = construct.Struct(
	'opcode' / PackEnum(Opcode),
)