import construct

from .headers import ServerHeader
from ..opcode import Opcode

SMSG_WARDEN_DATA = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_WARDEN_DATA, size=39),
	'command' / construct.Byte,
	# 'command' / PackEnum(warden.ServerCommand),
	# 'request' / construct.Switch(
	# 	construct.this.command, {
	# 		warden.ServerCommand.module_use: warden.ServerModuleInfoRequest,
	# 		warden.ServerCommand.module_cache: warden.ServerModuleTransferRequest,
	# 		warden.ServerCommand.cheat_checks_request: warden.CheatChecksRequest,
	# 		warden.ServerCommand.module_initialize: warden.InitModuleRequest,
	# 		warden.ServerCommand.hash_request: warden.ServerHashRequest
	# 	}
	# )
)
