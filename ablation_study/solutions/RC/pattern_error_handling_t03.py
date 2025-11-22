from typing import Callable, Any
import time

def retry_operation(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    base_delay: float = 1.0
) -> tuple[bool, Any]:
    """
    Retry operation with exponential backoff.

    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            result = operation()
            return (True, result)
        except Exception as e:
            last_exception = e
            # Only delay if not the last attempt
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)

    return (False, last_exception)
