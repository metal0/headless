import esper

from pont.client.world.game.position import Position
from pont.client.world.game.screen import Screen

from pont import log
log = log.get_logger(__name__)

class Game:
	def __init__(self, context, world_session):
		self.context = context
		self.world_session = world_session
		self.world = esper.World()
		self.local_player = self.world.create_entity(Position(0, 0, 0))
		self.screen = Screen.character_screen
		# self.context.emitter.emit(events.)

	def run(self):
		pass