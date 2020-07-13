import construct

from pont.client.world.guid import Guid
from pont.utility.construct import GuidConstruct, PackEnum
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...guild.events import GuildEventType
from ...guild.guild import GuildInfo
from ...guild.roster import GuildRankData, RosterMemberData

CMSG_GUILD_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_INVITE, 48),
	'name' / construct.PaddedString(48, 'ascii'),
)

CMSG_GUILD_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_QUERY, 4),
	'guild_id' / construct.Int32ul,
)

CMSG_GUILD_ROSTER = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_ROSTER, 0)
)

CMSG_GUILD_CREATE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_CREATE, 8),
	'guild_name' / construct.CString('ascii')
)

SMSG_GUILD_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_QUERY_RESPONSE, 96),
	'info' / GuildInfo
)

SMSG_GUILD_INFO = construct.Struct(
	'header' / ClientHeader(Opcode.SMSG_GUILD_INFO, 0),
	'guild_name' / construct.CString('ascii'),
	'create_date' / construct.Byte,
	'num_members' / construct.Int32ul,
	'num_accounts' / construct.Int32ul
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
	'guid' / construct.Switch(
		construct.this.type, {
			GuildEventType.joined: construct.ByteSwapped(GuidConstruct(Guid)),
			GuildEventType.left: construct.ByteSwapped(GuidConstruct(Guid)),
			GuildEventType.signed_on: construct.ByteSwapped(GuidConstruct(Guid)),
			GuildEventType.signed_off: construct.ByteSwapped(GuidConstruct(Guid)),
		}
	)
)

SMSG_GUILD_ROSTER = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_ROSTER, 0),
	'total_members' / construct.Int32ul,
	'motd' / construct.CString('ascii'),
	'guild_info' / construct.CString('ascii'),
	'ranks' / construct.PrefixedArray(construct.Int32ul, GuildRankData),
	'members' / construct.Array(construct.this.total_members, RosterMemberData)
)
