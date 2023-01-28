from enum import Enum


class GuildEventType(Enum):
    promotion = 0
    demotion = 1
    motd = 2
    joined = 3
    left = 4
    removed = 5
    leader_is = 6
    leader_changed = 7
    disbanded = 8
    tabard_change = 9
    rank_updated = 10
    rank_deleted = 11
    signed_on = 12
    signed_off = 13

    bank_bag_slots_changed = 14
    bank_tab_purchased = 15
    bank_tab_updated = 16
    bank_money_set = 17
    bank_tab_and_money_updated = 18
    bank_text_changed = 19
