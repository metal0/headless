from enum import Enum

import construct


class GuildMemberDataType(Enum):
	zone_id = 1
	level = 2

class GuildCommandType(Enum):
	create = 0
	invite = 1
	quit = 3
	roster = 5
	promote = 6
	demote = 7
	remove = 8
	change_leader = 10
	edit_motd = 11
	guild_chat = 13
	founder = 14
	change_rank = 16
	public_note = 19
	view_tab = 21
	move_item = 22
	repair = 25

# noinspection PyTypeChecker
class GuildRankRights(Enum):
	empty = 0x00000040
	guild_chat_listen = empty | 0x00000001
	guild_chat_speak = empty | 0x00000002
	officer_chat_listen = empty | 0x00000004
	officer_chat_speak = empty | 0x00000008
	invite = empty | 0x00000010
	remove = empty | 0x00000020
	promote = empty | 0x00000080
	demote = empty | 0x00000100
	set_motd = empty | 0x00001000
	ep_note = empty | 0x00002000
	view_officer_note = empty | 0x00004000
	edit_officer_note = empty | 0x00008000
	modify_guild_info = empty | 0x00010000
	withdraw_gold_lock = 0x00020000
	withdraw_repair = 0x00040000
	withdraw_gold = 0x00080000
	create_guild_event = 0x00100000
	all = 0x001DF1FF

class Guild:
	max_ranks = 10
	min_ranks = 5

GuildInfo = construct.Struct(
	'guild_id' / construct.ByteSwapped(construct.Int),
	'name' / construct.CString('ascii'),
	'ranks' / construct.Array(Guild.max_ranks, construct.CString('ascii')),
	'emblem_style' / construct.ByteSwapped(construct.Int),
	'emblem_color' / construct.ByteSwapped(construct.Int),
	'border_style' / construct.ByteSwapped(construct.Int),
	'border_color' / construct.ByteSwapped(construct.Int),
	'background_color' / construct.ByteSwapped(construct.Int),
	'num_ranks' / construct.ByteSwapped(construct.Int),
)