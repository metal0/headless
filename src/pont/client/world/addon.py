import construct

from .. import log

log = log.mgr.get_logger(__name__)

AddonData = construct.Struct(
	'name' / construct.CString('ascii'),
	'enabled' / construct.Flag,
	'crc' / construct.Int,
	'unk' / construct.Int,
)

AddonsInfo = construct.Struct(
	'addons' / construct.PrefixedArray(construct.Int, AddonData),
	'unk' / construct.Int
)

class Addon:
	def __init__(self, name: str, enabled: bool = True, crc: int = 0, unk: int = 0):
		self.name = name
		self.enabled = enabled
		self.crc = crc
		self.unk = unk

class BlizzardAddons:
	AchievementUI = Addon(name='blizzard_AchievementUI', enabled=True, crc=0x4C1C776D)
	ArchaeologyUI = Addon(name='blizzard_ArchaeologyUI', enabled=True, crc=0x4C1C776D)
	ArenaUI = Addon(name='blizzard_ArenaUI', enabled=True, crc=0x4C1C776D)
	AuctionUI = Addon(name='blizzard_AuctionUI', enabled=True, crc=0x4C1C776D)
	BarbershopUI = Addon(name='blizzard_BarbershopUI', enabled=True, crc=0x4C1C776D)
	BattlefieldMinimap = Addon(name='blizzard_BattlefieldMinimap', enabled=True, crc=0x4C1C776D)
	BindingUI = Addon(name='blizzard_BindingUI', enabled=True, crc=0x4C1C776D)
	Calendar = Addon(name='blizzard_Calendar', enabled=True, crc=0x4C1C776D)
	ClientSavedVariables = Addon(name='blizzard_ClientSavedVariables', enabled=True, crc=0x4C1C776D)
	CombatLog = Addon(name='blizzard_CombatLog', enabled=True, crc=0x4C1C776D)
	CombatText = Addon(name='blizzard_CombatText', enabled=True, crc=0x4C1C776D)
	CompactRaidFrames = Addon(name='blizzard_CompactRaidFrames', enabled=True, crc=0x4C1C776D)
	CUFProfiles = Addon(name='blizzard_CUFProfiles', enabled=True, crc=0x4C1C776D)
	DebugTools = Addon(name='blizzard_DebugTools', enabled=True, crc=0x4C1C776D)
	EncounterJournal = Addon(name='blizzard_EncounterJournal', enabled=True, crc=0x4C1C776D)
	GlyphUI = Addon(name='blizzard_GlyphUI', enabled=True, crc=0x4C1C776D)
	GMChatUI = Addon(name='blizzard_GMChatUI', enabled=True, crc=0x4C1C776D)
	GMSurveyUI = Addon(name='blizzard_GMSurveyUI', enabled=True, crc=0x4C1C776D)
	GuildBankUI = Addon(name='blizzard_GuildBankUI', enabled=True, crc=0x4C1C776D)
	GuildControlUI = Addon(name='blizzard_GuildControlUI', enabled=True, crc=0x4C1C776D)
	GuildUI = Addon(name='blizzard_GuildUI', enabled=True, crc=0x4C1C776D)
	InspectUI = Addon(name='blizzard_InspectUI', enabled=True, crc=0x4C1C776D)
	ItemAlterationUI = Addon(name='blizzard_ItemAlterationUI', enabled=True, crc=0x4C1C776D)
	ItemSocketingUI = Addon(name='blizzard_ItemSocketingUI', enabled=True, crc=0x4C1C776D)
	LookingForGuildUI = Addon(name='blizzard_LookingForGuildUI', enabled=True, crc=0x4C1C776D)
	MacroUI = Addon(name='blizzard_MacroUI', enabled=True, crc=0x4C1C776D)
	MovePad = Addon(name='blizzard_MovePad', enabled=True, crc=0x4C1C776D)
	RaidUI = Addon(name='blizzard_RaidUI', enabled=True, crc=0x4C1C776D)
	ReforgingUI = Addon(name='blizzard_ReforgingUI', enabled=True, crc=0x4C1C776D)
	TalentUI = Addon(name='blizzard_TalentUI', enabled=True, crc=0x4C1C776D)
	TimeManager = Addon(name='blizzard_TimeManager', enabled=True, crc=0x4C1C776D)
	TokenUI = Addon(name='blizzard_TokenUI', enabled=True, crc=0x4C1C776D)
	TradeSkillUI = Addon(name='blizzard_TradeSkillUI', enabled=True, crc=0x4C1C776D)
	TrainerUI = Addon(name='blizzard_TrainerUI', enabled=True, crc=0x4C1C776D)
	VoidStorageUI = Addon(name='blizzard_VoidStorageUI', enabled=True, crc=0x4C1C776D)
