"""
Retry decorator with exponential backoff.
"""

import time
from functools import wraps
from typing import Callable, Any, Type, Union, Tuple
from utils import logger

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1,
    max_delay: float = 60,
    backoff_factor: float = 2,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
) -> Callable:
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplicative factor for delay after each retry
        exceptions: Exception or tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            
            for retry in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if retry == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded. Last error: {str(e)}")
                        raise
                    
                    logger.warning(f"Retry {retry + 1}/{max_retries} after error: {str(e)}")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            if last_exception:
                raise last_exception
            return None
        return wrapper
    return decorator 