import uuid
from enum import Enum

class AuthEvent(Enum):
	# Basic connection events
	connected = uuid.uuid4()
	data_received = uuid.uuid4()

	disconnected = uuid.uuid4()

	realmlist_ready = uuid.uuid4()

	#
	logging_in = uuid.uuid4()
	invalid_login = uuid.uuid4()
	login_success = uuid.uuid4()

auth = AuthEvent

class WorldEvent(Enum):
	# Basic Events
	connected = uuid.uuid4()
	in_queue = uuid.uuid4()
	logged_in = uuid.uuid4()
	loading_world = uuid.uuid4()
	ingame = uuid.uuid4()

	# Net events
	disconnected = uuid.uuid4()

	received_SMSG_AUTH_CHALLENGE = uuid.uuid4()
	received_SMSG_AUTH_RESPONSE = uuid.uuid4()
	received_SMSG_NAME_QUERY_RESPONSE = uuid.uuid4()
	received_SMSG_CHAR_ENUM = uuid.uuid4()
	received_SMSG_PONG = uuid.uuid4()
	received_SMSG_LOGIN_VERIFY_WORLD = uuid.uuid4()
	received_SMSG_WARDEN_DATA = uuid.uuid4()

	sent_CMSG_PING = uuid.uuid4()
	sent_CMSG_KEEP_ALIVE = uuid.uuid4()
	sent_CMSG_WARDEN_DATA = uuid.uuid4()
	sent_CMSG_CHAR_ENUM = uuid.uuid4()

world = WorldEvent

class ConsoleEvent(Enum):
	data_received = uuid.uuid4()

console = ConsoleEvent

class ConfigEvent(Enum):
	relogger_changed = uuid.uuid4()
	username_changed = uuid.uuid4()
	password_changed = uuid.uuid4()

	auth_server_address_changed = uuid.uuid4()
	character_name_changed = uuid.uuid4()
	realm_name_changed = uuid.uuid4()

config = ConfigEvent