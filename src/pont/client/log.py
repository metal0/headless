from loguru import logger

class LogManager:
	def __init__(self, level=None, log_path=None, client=None):
		self._client = client
		# self._level = level
		self._format = '{time} | {level} | {name} - {message}'

	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, level):
		self._level = level

	@property
	def format(self):
		return self._format

	@format.setter
	def format(self, format):
		self._format = format

def _config_logger():
	logger.level('PACKETS', no=38, color='<blue>', icon='PACKETS')
	logger.level('EVENTS', no=40, color='<yellow>', icon='EVENTS')
	# logger.


_config_logger()
