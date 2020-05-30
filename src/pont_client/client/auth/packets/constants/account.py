import construct

AccountType = construct.Enum(construct.Byte,
     player=0,
     moderator=1,
     game_master=2,
     administrator=3,
     console=4,
)
