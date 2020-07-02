import construct

from pont.utility.construct import GuidConstruct, PackEnum
from pont.client.world.guid import Guid
from .parse import parser
from .constants import Opcode
from .headers import ClientHeader, ServerHeader
from ...guild.events import GuildEventType
from ...guild.guild import GuildInfo
from ...guild.roster import GuildRankData, RosterMemberData

CMSG_GUILD_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_INVITE, 48),
	'name' / construct.PaddedString(48, 'ascii'),
)

CMSG_GUILD_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_QUERY, 4),
	'guild_id' / construct.ByteSwapped(construct.Int),
)

CMSG_GUILD_ROSTER = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_ROSTER, 0)
)

SMSG_GUILD_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_QUERY_RESPONSE, 96),
	'info' / GuildInfo
)

SMSG_GUILD_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_INVITE, 144),
	'inviter_name' / construct.CString('ascii'),
	'guild_name' / construct.CString('ascii')
)

SMSG_GUILD_EVENT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_EVENT, 19),
	'type' / PackEnum(GuildEventType),
	# TODO: Figure out what this is
	'parameters' / construct.PrefixedArray(construct.Byte, construct.CString(encoding='ascii')),
	'guid' / construct.ByteSwapped(GuidConstruct(Guid))
)

SMSG_GUILD_ROSTER = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_ROSTER, 0),
	'total_members' / construct.ByteSwapped(construct.Int),
	'motd' / construct.CString('ascii'),
	'guild_info' / construct.CString('ascii'),
	'ranks' / construct.PrefixedArray(construct.ByteSwapped(construct.Int), GuildRankData),
	'members' / construct.Array(construct.this.total_members, RosterMemberData)
)

parser.set_parser(Opcode.SMSG_GUILD_EVENT, SMSG_GUILD_EVENT)
parser.set_parser(Opcode.SMSG_GUILD_ROSTER, SMSG_GUILD_ROSTER)
parser.set_parser(Opcode.SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_QUERY_RESPONSE)