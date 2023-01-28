from enum import Enum


class GuildBank:
    max_tabs = 6
    max_slots = 98


class GuildBankRights(Enum):
    view_tab = 1
    put_item = 2
    update_text = 4
    deposit_item = view_tab | put_item
    full = 0xFF
