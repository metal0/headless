from enum import Enum

class AccountType(Enum):
     player=0
     moderator=1
     game_master=2
     administrator=3
     console=4

class AccountStatus(Enum):
     success = 0
     failure = 1

     unknown1 = 2 # Bad connection?
     account_banned = 3

     invalid_information = 4
     invalid_information2 = 5

     account_in_use = 6
     prepaid_limit_reached = 7

     server_full = 8
     wrong_build = 9
     update_client_version = 10

     unknown2 = 11 # Bad connection
     account_frozen = 12

     unknown3 = 13 # Bad connection
     unknown4 = 14 # Connected?
     parental_control_restriction = 15
