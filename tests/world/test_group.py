from wlink.world.packets import GroupType


def test_group_type():
	assert str(GroupType.normal) == 'GroupType.normal'
	assert str(GroupType.raid) == 'GroupType.raid'
	assert str(GroupType.lfg_restricted) == 'GroupType.lfg_restricted'
	assert str(GroupType.lfg) == 'GroupType.lfg'
	assert str(GroupType.bg_raid) == 'GroupType.bg_raid'
