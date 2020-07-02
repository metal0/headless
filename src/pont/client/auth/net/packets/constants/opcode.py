from enum import Enum

class Opcode(Enum):
	login_challenge = 0x00
	login_proof = 0x01

	reconnect_challenge = 0x02
	reconnect_proof = 0x03

	realm_list = 0x10

	xfer_initiate = 0x30
	xfer_data = 0x31
	xfer_accept = 0x32
	xfer_resume = 0x33
	xfer_cancel = 0x34
