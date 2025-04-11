"""
Rate limiting decorator implementation.
"""

import time
from functools import wraps
from typing import Callable, Dict, Any
from utils import logger

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = []

    def can_make_request(self) -> bool:
        current_time = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time <= self.time_window]
        
        # Check if we can make a new request
        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        return False

def rate_limit(max_requests: int, time_window: int = 3600) -> Callable:
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not limiter.can_make_request():
                logger.warning(f"Rate limit exceeded. Max {max_requests} requests per {time_window} seconds.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator 