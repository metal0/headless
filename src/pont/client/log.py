import logging
from loguru import logger

def _config_logger():
	logger.configure()
	logger.level('PACKETS', no=10, color='<blue>', icon='PACKETS')
	logger.level('EVENTS', no=15, color='<yellow>', icon='EVENTS')
	logger.level('MESSAGES', no=18, color='<green>', icon='MESSAGES')

_config_logger()
