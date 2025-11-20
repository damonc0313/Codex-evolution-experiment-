# Task: Retry with Exponential Backoff

Implement a function that retries an operation with exponential backoff.

**Function signature:**
```python
from typing import Callable, Any
import time

def retry_operation(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    base_delay: float = 1.0
) -> tuple[bool, Any]:
    """
    Retry operation with exponential backoff.

    Args:
        operation: Function to call (no arguments)
        max_attempts: Maximum number of attempts
        base_delay: Base delay in seconds (doubles each retry)

    Returns:
        Tuple of (success: bool, result: Any or exception)
    """
    pass
```

**Requirements:**
- Use try-except within a loop
- Delay between retries: base_delay * (2 ** attempt)
- Return (True, result) on success
- Return (False, exception) after all attempts fail
- Don't delay after the last failed attempt
