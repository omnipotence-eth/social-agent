from typing import Any, Optional
import time
from collections import OrderedDict
from config import settings
from utils import logger

class Cache:
    """LRU Cache implementation with TTL."""
    
    def __init__(self, max_size: int = settings.CACHE_MAX_SIZE, ttl: int = settings.CACHE_TTL):
        """Initialize the cache."""
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        try:
            if key in self.cache:
                # Check if the item has expired
                if time.time() - self.timestamps[key] > self.ttl:
                    self.delete(key)
                    return None
                
                # Move the item to the end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        try:
            # If the key exists, remove it first
            if key in self.cache:
                self.delete(key)
            
            # If the cache is full, remove the least recently used item
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            # Add the new item
            self.cache[key] = value
            self.timestamps[key] = time.time()
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        try:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")

    def clear(self) -> None:
        """Clear the cache."""
        try:
            self.cache.clear()
            self.timestamps.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def cleanup(self) -> None:
        """Clean up expired items."""
        try:
            current_time = time.time()
            expired_keys = [
                key for key, timestamp in self.timestamps.items()
                if current_time - timestamp > self.ttl
            ]
            for key in expired_keys:
                self.delete(key)
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")

# Create global cache instance
cache = Cache() 