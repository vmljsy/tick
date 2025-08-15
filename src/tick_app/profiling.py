import logging
import time
from functools import wraps

from .services.config_service import config_service

logger = logging.getLogger(__name__)

def profile_time(func):
    """
    A decorator that logs the execution time of a function if debug_mode is enabled.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug_mode = config_service.get("debug_mode")
        if debug_mode and debug_mode.lower() == "true":
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000 # in milliseconds
            logger.debug(f"Function '{func.__name__}' executed in {execution_time:.2f} ms")
            return result
        else:
            return func(*args, **kwargs)
    return wrapper
