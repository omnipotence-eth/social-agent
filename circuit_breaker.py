from typing import Any, Callable, Optional, Type
from functools import wraps
import time
from enum import Enum
from utils import logger

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

class CircuitBreaker:
    """Circuit breaker implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    def can_execute(self) -> bool:
        """Check if the protected function can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
            
        return True  # HALF_OPEN state

    def record_success(self) -> None:
        """Record a successful execution."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        logger.info("Circuit breaker reset after successful execution")

    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: Type[Exception] = Exception
) -> Callable:
    """Circuit breaker decorator."""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not breaker.can_execute():
                raise Exception(
                    f"Circuit breaker is {breaker.state.value}, "
                    f"waiting {breaker.recovery_timeout}s for recovery"
                )
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except breaker.expected_exception as e:
                breaker.record_failure()
                raise
                
        return wrapper
    return decorator

# Example usage:
# @circuit_breaker(failure_threshold=5, recovery_timeout=60)
# def api_call():
#     pass 