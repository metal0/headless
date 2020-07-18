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
	logging_in = uuid.uuid4()
	loading_world = uuid.uuid4()
	entered_world = uuid.uuid4()
	logged_out = uuid.uuid4()

	# Net events
	disconnected = uuid.uuid4()

	received_group_invite = uuid.uuid4()
	received_guild_invite = uuid.uuid4()

	received_chat_message = uuid.uuid4()
	received_gm_chat_message = uuid.uuid4()
	received_duel_request = uuid.uuid4()
	received_name_query_response = uuid.uuid4()

	received_packet = uuid.uuid4()
	received_SMSG_AUTH_CHALLENGE = uuid.uuid4()
	received_SMSG_AUTH_RESPONSE = uuid.uuid4()
	received_SMSG_CHAR_ENUM = uuid.uuid4()
	received_SMSG_PONG = uuid.uuid4()
	received_SMSG_LOGIN_VERIFY_WORLD = uuid.uuid4()
	received_warden_data = uuid.uuid4()
	received_tutorial_flags = uuid.uuid4()
	received_time_sync_request = uuid.uuid4()
	received_logout_response = uuid.uuid4()
	logout_cancelled = uuid.uuid4()

	sent_CMSG_PING = uuid.uuid4()
	sent_CMSG_KEEP_ALIVE = uuid.uuid4()
	sent_CMSG_WARDEN_DATA = uuid.uuid4()
	sent_CMSG_CHAR_ENUM = uuid.uuid4()
	sent_CMSG_TIME_SYNC_RES = uuid.uuid4()
	sent_CMSG_PLAYER_LOGIN = uuid.uuid4()
	sent_CMSG_LOGOUT_REQUEST = uuid.uuid4()
	sent_CMSG_LOGOUT_CANCEL = uuid.uuid4()
	sent_CMSG_AUTH_SESSION = uuid.uuid4()

world = WorldEvent

class ConfigEvent(Enum):
	relogger_changed = uuid.uuid4()
	username_changed = uuid.uuid4()
	password_changed = uuid.uuid4()

	auth_server_address_changed = uuid.uuid4()
	character_name_changed = uuid.uuid4()
	realm_name_changed = uuid.uuid4()

config = ConfigEvent