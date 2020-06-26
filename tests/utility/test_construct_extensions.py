import hashlib
import hmac

import construct

from pont_client.cryptography.rc4 import RC4
from pont_client.utility.construct import AddressPort, RC4Encrypted
from pont_client.utility.string import int_to_bytes

def test_address_port():
	# Test big endian encoding and decoding
	con = AddressPort()
	address = ('127.0.0.1', 8085)
	address_packed = con.build(address)

	assert address_packed == b'127.0.0.1:8085\x00'
	assert ('127.0.0.1', 8085) == con.parse(address_packed)

def test_address_port2():
	# Test composability with other constructs
	addr_con = AddressPort()
	Test = construct.Sequence(
		construct.CString('ascii'),
		addr_con,
		construct.Int
	)

	data = Test.build(['hey there', ('127.0.0.1', 8085), 7])
	assert data  == b'hey there\x00127.0.0.1:8085\x00\x00\x00\x00\x07'
	assert Test.parse(data) == ['hey there', ('127.0.0.1', 8085), 7]

def test_RC4Encrypted():
	client_hmac_key = bytes.fromhex('C2B3723CC6AED9B5343C53EE2F4367CE')
	server_hmac_key = bytes.fromhex('CC98AE04E897EACA12DDC09342915357')
	session_key = 1663409584630047000777877231362896553203558282147253922228135029179872380738266872792639955976101

	client_key = hmac.new(key=client_hmac_key, digestmod=hashlib.sha1)
	client_key.update(int_to_bytes(session_key))
	# encrypter = RC4()
	# encrypter.set_key(client_key.digest())
	# encrypter.update(bytes([0]*1024))

	server_key = hmac.new(key=server_hmac_key, digestmod=hashlib.sha1)
	server_key.update(int_to_bytes(session_key))
	# decrypter = RC4()
	# decrypter.set_key(server_key.digest())
	# decrypter.update(bytes([0]*1024))

	# decrypter = arc4.ARC4(server_key.digest())
	decrypter = RC4(server_key.digest())
	encrypter = RC4(client_key.digest())

	# encrypter = arc4.ARC4(client_key.digest())
	encrypter.encrypt(bytes([0]*1024))
	decrypter.encrypt(bytes([0]*1024))

	encrypt = lambda data: encrypter.encrypt(data)
	decrypt = lambda data: decrypter.encrypt(data)
	enc_con = lambda subcon: RC4Encrypted(subcon, encrypt, decrypt, size=4)

	# con_encrypted = ServerHeader().build({
	# 	'opcode': Opcode.CMSG_PING,
	# 	'size': 2
	# })
	#
	# original = ServerHeader().build({
	# 	'opcode': Opcode.CMSG_PING,
	# 	'size': 2
	# })

	original = 'hey there'.encode()
	print(f'{original=}')

	encrypted = encrypt(original)
	print(f'{encrypted=}')

	decrypted = decrypt(encrypted)
	print(f'{decrypted=}')

	# parsed = enc_con(ServerHeader())
	# print(f'parsed: {parsed}')
	# assert parsed.opcode == Opcode.CMSG_PING
	# assert parsed.size == 2

