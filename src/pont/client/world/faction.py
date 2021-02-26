from typing import NamedTuple

import construct
from enum import Enum

from pont.utility.construct import PackEnum

class FactionFlags(Enum):
    none               = 0x00                 # no faction flag
    visible            = 0x01                 # makes visible in client (set or can be set at interaction with target of this faction)
    at_war             = 0x02                 # enable AtWar-button in client. player controlled (except opposition team always war state), Flag only set on initial creation
    hidden             = 0x04                 # hidden faction from reputation pane in client (player can gain reputation, but this update is not sent to client)
    invisible_forced   = 0x08                 # always overwrite FACTION_FLAG_VISIBLE and hide faction in rep.list, used for hide opposite team factions
    peace_forced       = 0x10                 # always overwrite FACTION_FLAG_AT_WAR, used for prevent war with own team factions
    inactive           = 0x20                 # player controlled, state stored in characters.data (CMSG_SET_FACTION_INACTIVE)
    rival              = 0x40                 # flag for the two competing outland factions
    special            = 0x80                 # horde and alliance home cities and their northrend allies have this flag

FactionState = construct.Struct(
	'flags' / PackEnum(FactionFlags, construct.Byte),
	'standing' / construct.Int32ul # the player's standing with a faction (how well a faction likes you)
)
