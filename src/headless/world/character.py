from typing import Optional

from wlink import Guid
from wlink.utility.construct import Coordinates
from wlink.world.packets import Race, CombatClass, make_CMSG_CHAR_RENAME, CMSG_CHAR_RENAME, make_CMSG_CHAR_CREATE, \
	CMSG_CHAR_CREATE

from headless import events

class Character:
	def __init__(self, world, info):
		self._info = info
		self._world = world

	def __str__(self):
		return f'{self.name} ({self.guid}) Level {self.level} {self.race} {self.combat_class}'

	async def rename(self, new_name: str):
		await self._world.stream.send_encrypted_packet(CMSG_CHAR_RENAME, make_CMSG_CHAR_RENAME(new_name=new_name, guid=self.guid))
		self._world.emitter.emit(events.world.sent_character_rename)

	async def create(self, name: str):
		await self._world.stream.send_encrypted_packet(CMSG_CHAR_CREATE, make_CMSG_CHAR_CREATE(name=name))
		self._world.emitter.emit(events.world.sent_character_create)

	@property
	def guid(self) -> Guid:
		return self._info.guid

	@property
	def name(self) -> str:
		return self._info.name

	@property
	def race(self) -> Race:
		return self._info.race

	@property
	def combat_class(self) -> CombatClass:
		return self._info.combat_class

	@property
	def gender(self):
		return self._info.gender

	@property
	def skin(self):
		return self._info.skin

	@property
	def face(self):
		return self._info.face

	@property
	def hair_style(self):
		return self._info.hair_style

	@property
	def hair_color(self):
		return self._info.hair_color

	@property
	def facial_hair(self):
		return self._info.facial_hair

	@property
	def level(self) -> int:
		return self._info.level

	@property
	def zone(self):
		return self._info.zone

	@property
	def map(self):
		return self._info.map

	@property
	def position(self) -> Coordinates:
		return self._info.position

	@property
	def guild_guid(self) -> Optional[Guid]:
		return self._info.guild_guid

	@property
	def flags(self):
		return self._info.flags

	@property
	def customization_flags(self):
		return self._info.customization_flags

	@property
	def is_first_login(self) -> bool:
		return self._info.is_first_login

	@property
	def pet(self):
		return self._info.pet

	@property
	def items(self):
		return self._info.items

	@property
	def bags(self):
		return self._info.bags
