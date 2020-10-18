class AuthError(Exception):
	pass

class InvalidLogin(AuthError):
	pass

class ProtocolError(AuthError):
	pass