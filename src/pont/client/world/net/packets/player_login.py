import construct

from pont.client.world.guid import Guid
from pont.client.world.net.packets.constants import Opcode
from pont.client.world.net.packets.headers import ClientHeader
from pont.utility.construct import GuidConstruct

CMSG_PLAYER_LOGIN = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PLAYER_LOGIN, 8),
	'player_guid' / construct.ByteSwapped(GuidConstruct(Guid))
)