from wlink.world.packets import GroupType


class GroupMember:
    def __init__(self, packet):
        self._packet = packet

    def __str__(self):
        online_string = "Online" if self.online else "Offline"
        return f"{self.name} ({online_string})"

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self._packet.name

    @property
    def guid(self):
        return self._packet.guid

    @property
    def online(self) -> bool:
        return self._packet.online


class Group:
    def __init__(self, world, packet=None):
        self.world = world
        self._packet = packet

    def update(self, packet=None):
        self._packet = packet

    @property
    def is_empty(self) -> bool:
        return self._packet is not None

    @property
    def leader(self):
        return self._packet.leader_guid

    @property
    def type(self):
        if self._packet is None:
            return GroupType.party

        for data in GroupType:
            if data.name != "party" and getattr(self._packet.type, data.name, None):
                return data

        return GroupType.party

    @property
    def members(self):
        if self._packet is None:
            return []
        return [GroupMember(member_packet) for member_packet in self._packet.members]

    @property
    def size(self):
        if self._packet is None:
            return 0

        return self._packet.size

    def __len__(self):
        return self.size
