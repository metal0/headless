import construct

from pont.utility.construct import PackEnum, GuidConstruct
from ..opcode import Opcode
from .headers import ClientHeader, ServerHeader
from ...guid import Guid
from ...chat.message import MessageType, MonsterMessage, WhisperForeign, BGMessage, AchievementMessage, DefaultMessage, \
	ChannelMessage
from ...language import Language

CMSG_MESSAGECHAT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_MESSAGECHAT, 0),
	'type' / PackEnum(MessageType, construct.Int32sl),
	'language' / PackEnum(Language, construct.Int32sl)
)

def make_messagechat_packet(gm_chat=False):
	return construct.Struct(
		'header' / ServerHeader(Opcode.SMSG_GM_MESSAGECHAT if gm_chat else Opcode.SMSG_MESSAGECHAT, 0),
		'type' / PackEnum(MessageType, construct.Int8sl),
		'language' / PackEnum(Language, construct.Int32sl),
		'sender_guid' / GuidConstruct(Guid),
		'flags' / construct.Default(construct.Int32ul, 0),
		'info' / construct.Switch(
			construct.this.type, {
				MessageType.monster_say: MonsterMessage,
				MessageType.monster_emote: MonsterMessage,
				MessageType.monster_party: MonsterMessage,
				MessageType.monster_yell: MonsterMessage,
				MessageType.monster_whisper: MonsterMessage,
				MessageType.raid_boss_emote: MonsterMessage,
				MessageType.raid_boss_whisper: MonsterMessage,

				MessageType.whisper_foreign: WhisperForeign,

				MessageType.bg_system_alliance: BGMessage,
				MessageType.bg_system_horde: BGMessage,
				MessageType.bg_system_neutral: BGMessage,

				MessageType.achievement: AchievementMessage,
				MessageType.guild_achievement: AchievementMessage,

				MessageType.channel: ChannelMessage(gm_chat=gm_chat),

			}, default=DefaultMessage(gm_chat=gm_chat)
		),

		'message' / construct.Prefixed(construct.Int32ul, construct.CString('utf-8')),
		'chat_tag' / construct.Byte,
		'achievement_id' / construct.Switch(
			construct.this.type, {
				MessageType.achievement: construct.Int32ul,
				MessageType.guild_achievement: construct.Int32ul,
			}
		)
	)

SMSG_GM_MESSAGECHAT = make_messagechat_packet(gm_chat=True)
SMSG_MESSAGECHAT = make_messagechat_packet(gm_chat=False)