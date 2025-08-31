import logging
from .services.config_service import config_service

def setup_logging():
    debug_mode = config_service.get("debug_mode")
    if debug_mode and debug_mode.lower() == "true":
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setup_logging()
