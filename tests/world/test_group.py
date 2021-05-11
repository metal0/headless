from wlink.world.packets import GroupType


def test_group_type():
	assert str(GroupType.party) == 'party'
	assert str(GroupType.raid) == 'raid'
	assert str(GroupType.lfg_restricted) == 'lfg_restricted'
	assert str(GroupType.lfg) == 'lfg'
	assert str(GroupType.bg_raid) == 'bg_raid'
