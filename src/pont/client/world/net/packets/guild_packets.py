import construct

from pont.utility.construct import GuidConstruct, PackEnum
from pont.client.world.guid import Guid
from .headers import ServerHeader, ClientHeader
from ..opcode import Opcode
from ...guild.events import GuildEventType
from ...guild.guild import GuildCommandType, GuildCommandError, Guild
from ...guild.roster import GuildRankData, RosterMemberData

CMSG_GUILD_QUERY = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_QUERY, 4),
	'guild_id' / construct.Int32ul,
)

CMSG_GUILD_ROSTER = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_ROSTER, 0)
)

SMSG_GUILD_ROSTER = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_ROSTER, 0),
	'total_members' / construct.Int32ul,
	'motd' / construct.CString('ascii'),
	'guild_info' / construct.CString('ascii'),
	'ranks' / construct.PrefixedArray(construct.Int32ul, GuildRankData),
	'members' / construct.Array(construct.this.total_members, RosterMemberData)
)

CMSG_GUILD_CREATE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_CREATE, 8),
	'guild_name' / construct.CString('ascii')
)

CMSG_GUILD_ACCEPT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_ACCEPT, 0)
)

CMSG_GUILD_DECLINE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_DECLINE, 0)
)

CMSG_GUILD_SET_PUBLIC_NOTE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_SET_PUBLIC_NOTE, 10),
	'player' / construct.CString('ascii'),
	'note' / construct.CString('ascii')
)

SMSG_GUILD_COMMAND_RESULT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_COMMAND_RESULT, 8 + 1),
	'command_type' / PackEnum(GuildCommandType, construct.Int32ul),
	'parameters' / construct.CString('utf-8'),
	'error_code' / PackEnum(GuildCommandError, construct.Int32ul),
)

CMSG_GUILD_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GUILD_INVITE, 48),
	'name' / construct.PaddedString(48, 'ascii'),
)

SMSG_GUILD_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_INVITE, 10),
	'inviter' / construct.CString('ascii'),
	'guild' / construct.CString('ascii')
)

SMSG_GUILD_EVENT = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_EVENT, 19),
	'type' / PackEnum(GuildEventType),
	# TODO: Figure out what this is
	'parameters' / construct.PrefixedArray(construct.Byte, construct.CString(encoding='ascii')),
	'guid' / construct.Switch(
		construct.this.type, {
			GuildEventType.joined: GuidConstruct(Guid),
			GuildEventType.left: GuidConstruct(Guid),
			GuildEventType.signed_on: GuidConstruct(Guid),
			GuildEventType.signed_off: GuidConstruct(Guid),
		}
	)
)

SMSG_GUILD_QUERY_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GUILD_QUERY_RESPONSE, 4 + 0 + Guild.max_ranks * 0 + 4 * 6),
	'guild_id' / construct.Int32ul,
	'name' / construct.CString('ascii'),
	'ranks' / construct.Array(Guild.max_ranks, construct.CString('ascii')),
	'emblem_style' / construct.Int32ul,
	'emblem_color' / construct.Int32ul,
	'border_style' / construct.Int32ul,
	'border_color' / construct.Int32ul,
	'background_color' / construct.Int32ul,
	'num_ranks' / construct.Int32ul,
)

SMSG_GUILD_INFO = construct.Struct(
	'header' / ClientHeader(Opcode.SMSG_GUILD_INFO, 0 + 1 + 4 + 4),
	'guild' / construct.CString('ascii'),
	'created' / construct.Byte,
	'num_members' / construct.Int32ul,
	'num_accounts' / construct.Int32ul
)