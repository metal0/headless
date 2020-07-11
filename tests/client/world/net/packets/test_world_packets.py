from pont.client import world
from pont.client.world.entities.player import Race, Gender, CombatClass
from pont.client.world.guid import Guid, GuidType

def test_SMSG_LOGIN_VERIFY_WORLD():
	data = bytes.fromhex('00163602010000006B65B7457FB382C544B7CE44A0F84540')
	packet = world.net.packets.SMSG_LOGIN_VERIFY_WORLD.parse(data)
	assert packet.map == 1
	assert packet.position.x == 1653.72705078125
	assert packet.position.y == -4182.43701171875
	assert packet.position.z == 5868.67724609375
	assert packet.rotation == 3.0932998657226562
	print(packet)

def test_SMSG_CLIENTCACHE_VERSION():
	data = bytes.fromhex('0006AB0403000000')
	packet = world.net.packets.SMSG_CLIENTCACHE_VERSION.parse(data)
	assert packet.version == 3
	print(packet)

def test_SMSG_WARDEN_DATA():
	data = bytes.fromhex('0022E6026CA213466EB28B199C9CBBA176D81DB89558D8ABDFBC65D71ABFF97183873601')
	packet = world.net.packets.SMSG_WARDEN_DATA.parse(data)
	print(packet)

def test_SMSG_TUTORIAL_FLAGS():
	data = bytes.fromhex('0022FD00F7BFEFFCE3A3F503000000000000000000000000000000000000000000000000')
	packet = world.net.packets.SMSG_TUTORIAL_FLAGS.parse(data)
	print(packet)

def test_SMSG_ADDON_INFO():
	data = bytes.fromhex('00BEEF020201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000002010000000000000201000000000000020100000000000000000000')
	packet = world.net.packets.SMSG_ADDON_INFO.parse(data)
	print(packet)

def test_SMSG_CHAR_ENUM():
	data = bytes.fromhex('03423B0003CC72330000000007537465616B6F000607000A04000106011100000001000000AA83B8C477C605C5ABC3BA42000000700000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000004A27000004000000000000000000000000000000000000000000004227000007000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004A14000015000000002A4900000E0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000087EA4A000000000753646764666A676B6A000B0501010507060101C40D0000120200003D9A77C5CDAC59C6E13AC94200000070000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A609000004000000002A8D00001400000000000000000000000000BC0C00000700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000624800001100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000C2E14E0000000007526F676D6F6F000404010504030507097906000001000000D2211846F0672745E598A44400000070000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000B22600000400000000000000000000000000E32000000600000000374200000700000000BB26000008000000000000000000000000008F1E00000A00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FA5000001100000000000000000000000000FB9C0000190000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
	char_enum = world.net.packets.SMSG_CHAR_ENUM.parse(data)
	print(f'{char_enum}')

	steako = char_enum.characters[0]
	assert steako.guid == Guid(value=0x7000000003372cc)
	assert steako.race == Race.tauren
	assert steako.gender == Gender.male
	assert steako.combat_class == CombatClass.shaman
	assert steako.skin == 10
	assert steako.face == 4
	assert steako.hair_style == 0
	assert steako.hair_color == 1
	assert steako.facial_hair == 6
	assert steako.level == 1
	assert steako.zone == 17
	assert steako.map == 1

	sdgdfjgkj = char_enum.characters[1]
	assert sdgdfjgkj.name == 'Sdgdfjgkj'
	assert sdgdfjgkj.race == Race.draenai
	assert sdgdfjgkj.combat_class == CombatClass.priest
	assert sdgdfjgkj.gender == Gender.female
	assert sdgdfjgkj.skin == 1
	assert sdgdfjgkj.face == 5
	assert sdgdfjgkj.hair_style == 7
	assert sdgdfjgkj.hair_color == 6
	assert sdgdfjgkj.level == 1
	assert sdgdfjgkj.zone == 3524
	assert sdgdfjgkj.map == 530
	assert sdgdfjgkj.position.x == 100.61499786376953
	assert sdgdfjgkj.position.y == -13931.2001953125
	assert sdgdfjgkj.position.z == -3961.639892578125

	rogmoo = char_enum.characters[2]
	assert rogmoo.name == 'Rogmoo'
	assert rogmoo.race == Race.night_elf
	assert rogmoo.combat_class == CombatClass.rogue
	assert rogmoo.gender == Gender.female
	assert rogmoo.skin == 5
	assert rogmoo.face == 4
	assert rogmoo.hair_style == 3
	assert rogmoo.hair_color == 5
	assert rogmoo.facial_hair == 7
	assert rogmoo.level == 9
	assert rogmoo.zone == 1657
	assert rogmoo.map == 1

	data2 = bytes.fromhex('01143B00010100000000000000416374000109010202080902506A020000010000006B65B7457FB382C544B7CE4401000000000000020000000000000000000000000000000000209E00000100000000000000000000000000EC9E00000300000000A81E00000400000000229E000014000000000000000000000000007601000007000000001256000008000000000000000000000000001F9E00000A000000000000000000000000000000000000000000000000000000000000000000000000000000007BF000001000000000000000000000000000000000000000000000000000000000000000000000000000000000B82C00001200000000000000000000000000000000000000000000000000000000000000')
	char_enum2 = world.net.packets.SMSG_CHAR_ENUM.parse(data2)
	print(f'{char_enum2}')

	act = char_enum2.characters[0]
	assert act.name == 'Act'
	assert act.race == Race.human
	assert act.combat_class == CombatClass.warlock
	assert act.gender == Gender.female
	assert act.skin == 2
	assert act.face == 2
	assert act.hair_style == 8
	assert act.hair_color == 9
	assert act.facial_hair == 2
	assert act.level == 80
	assert act.zone == 618
	assert act.map == 1

def test_CMSG_CHAR_ENUM():
	data = bytes.fromhex('000437000000')
	char_enum_request = world.net.packets.CMSG_CHAR_ENUM.parse(data)
	print(f'{char_enum_request}')

def test_CMSG_PLAYER_LOGIN():
	data = bytes.fromhex('000C3D0000000100000000000000')
	packet = world.net.packets.CMSG_PLAYER_LOGIN.parse(data)
	assert packet.player_guid == Guid(counter=1, type=GuidType.player)
	print(packet)

def test_SMSG_TIME_SYNC_REQ():
	data = bytes.fromhex('000690033E010000')
	packet = world.net.packets.SMSG_TIME_SYNC_REQ.parse(data)
	assert packet.header.size == 6
	assert packet.id == 318
	print(packet)

	data2 = b'\x00\x06\x90\x03\x19\x00\x00\x00'
	packet2 = world.net.packets.SMSG_TIME_SYNC_REQ.parse(data2)
	assert packet2.header.size == 6
	assert packet2.id == 25
	print(packet2)

	data3 = b'\x00\x06\x90\x03g\x00\x00\x00'
	packet3 = world.net.packets.SMSG_TIME_SYNC_REQ.parse(data3)
	assert packet3.header.size == 6
	print(packet3)

	data4 = b'\x00\x06\x90\x03h\x00\x00\x00'
	packet4 = world.net.packets.SMSG_TIME_SYNC_REQ.parse(data4)
	assert packet4.header.size == 6
	assert packet3.id == packet4.id - 1
	print(packet4)

def test_CMSG_TIME_SYNC_REQ():
	data = bytes.fromhex('000A9103000005000000D5C30000')
	packet = world.net.packets.CMSG_TIME_SYNC_RESP.parse(data)
	assert packet.header.size == 10
	assert packet.id == 5
	assert packet.client_ticks == 50133
	print(packet)

def test_CMSG_NAME_QUERY():
	data = bytes.fromhex('000C500000001F00000000000000')
	packet = world.net.packets.CMSG_NAME_QUERY.parse(data)
	assert packet.guid == Guid(counter=0x1f)
	print(packet)

def test_SMSG_NAME_QUERY():
	data = bytes.fromhex('000E5100011F0045636F000001010400')
	packet = world.net.packets.SMSG_NAME_QUERY_RESPONSE.parse(data)
	print(packet)

	assert packet.name_known == True
	assert packet.name == 'Eco'
	assert packet.realm_name == 'AzerothCore'
	assert packet.race == Race.human
	assert packet.gender == Gender.female

def test_SMSG_INIT_WORLD_STATES():
	data = bytes.fromhex('0050C20200000000EF050000EF0500000800D808000000000000D708000000000000D608000000000000D508000000000000D408000000000000D308000000000000770C0000010000003D0F000008000000')
	packet = world.net.packets.SMSG_INIT_WORLD_STATES.parse(data)
	print(packet)

def test_SMSG_BIND_POINT_UPDATE():
	data = bytes.fromhex('00165501CDD70BC6357E04C3F90FA742000000000C000000')
	packet = world.net.packets.SMSG_BIND_POINT_UPDATE.parse(data)
	print(packet)