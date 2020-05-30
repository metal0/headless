import construct

SecurityFlag = construct.Enum(construct.Byte,
	none=0x00,
	pin=0x01,
	matrix=0x02,
	token=0x04,
)