from enum import Enum

class Response(Enum):
      success = 0x00
      banned = 0x03
      unknown_account = 0x04
      incorrect_password = 0x05
      already_online = 0x06
      no_time = 0x07
      db_busy = 0x08
      version_invalid = 0x09
      version_update = 0x0A
      invalid_server = 0x0B
      suspended = 0x0C
      fail_noaccess = 0x0D
      success_survey = 0x0E
      parent_control = 0x0F
      locked_enforced = 0x10
      trial_ended = 0x11
      use_battlenet = 0x12
      anti_indulgence = 0x13
      expired = 0x14
      no_game_account = 0x15
      chargeback = 0x16
      internet_game_room_without_bnet = 0x17
      game_account_locked = 0x18
      unlockable_lock = 0x19
      conversion_required = 0x20
      disconnected = 0xFF
