import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

# Configure logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration with the specified log level."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler("social_agent.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("social_agent")

logger = setup_logging()

class RateLimiter:
    """Rate limiter implementation using token bucket algorithm with multiple time windows."""
    def __init__(self, limits: Dict[str, Dict[str, int]]):
        """
        Initialize rate limiter with multiple time windows.
        limits format: {
            '15m': {'max_requests': 50, 'time_window': 900},
            '1d': {'max_requests': 500, 'time_window': 86400},
            '30d': {'max_requests': 1000, 'time_window': 2592000}
        }
        """
        self.limits = limits
        self.tokens = {window: limit['max_requests'] for window, limit in limits.items()}
        self.last_update = {window: time.time() for window in limits.keys()}

    def acquire(self) -> bool:
        """Acquire a token if available in all time windows."""
        now = time.time()
        
        # Check all time windows
        for window, limit in self.limits.items():
            time_passed = now - self.last_update[window]
            self.tokens[window] = min(
                limit['max_requests'],
                self.tokens[window] + (time_passed * limit['max_requests'] / limit['time_window'])
            )
            self.last_update[window] = now

            if self.tokens[window] < 1:
                logger.warning(f"Rate limit exceeded for {window} window")
                return False

        # If we have tokens in all windows, use them
        for window in self.limits.keys():
            self.tokens[window] -= 1
        return True

def rate_limit(max_requests: int, time_window: int = 3600):
    """Rate limiting decorator."""
    def decorator(func):
        # Store request timestamps
        requests = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old requests outside the time window
            while requests and requests[0] < now - time_window:
                requests.pop(0)
                
            # Check if we've exceeded the rate limit
            if len(requests) >= max_requests:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
                
            # Add current request timestamp
            requests.append(now)
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

def retry_with_backoff(max_retries: int = 3, initial_delay: int = 1) -> Callable:
    """Decorator for retrying function calls with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
            
            logger.error(f"All retries failed for {func.__name__}: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

def sanitize_text(text: str, max_length: int = 280) -> str:
    """Sanitize and truncate text for safe posting."""
    # Remove potentially harmful characters
    text = "".join(char for char in text if char.isprintable())
    # Truncate to max length
    return text[:max_length].strip()

def save_to_json(data: Dict, filename: str) -> None:
    """Save data to a JSON file with proper error handling."""
    try:
        Path("data").mkdir(exist_ok=True)
        with open(f"data/{filename}", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving to JSON: {str(e)}")
        raise

def load_from_json(filename: str) -> Optional[Dict]:
    """Load data from a JSON file with proper error handling."""
    try:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filename}")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        raise

def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()