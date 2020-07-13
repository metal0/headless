from loguru import logger

class LogManager:
	def __init__(self, active_level='DEBUG', log_path=None, client=None):
		self._client = client
		self._active_level = active_level
		self._format = '[{time}] [{level}] [{name}] {message}'
		self.log_path = log_path

	@property
	def format(self):
		return self._format

	@format.setter
	def format(self, format):
		self._format = format

