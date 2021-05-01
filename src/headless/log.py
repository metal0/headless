from wlink.log import logger

def _configure_log(logger=logger, warden_level=15):
    logger.level('WARDEN', no=warden_level, color='<red>', icon='WARDEN')

_configure_log()

_ALL__ = ['logger']