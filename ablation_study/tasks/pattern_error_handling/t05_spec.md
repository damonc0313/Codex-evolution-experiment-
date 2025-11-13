# Task: Resource Manager with Cleanup

Implement a function that safely uses a resource and guarantees cleanup.

**Function signature:**
```python
from typing import Any, Callable

def safe_resource_use(
    acquire: Callable[[], Any],
    use: Callable[[Any], Any],
    release: Callable[[Any], None]
) -> tuple[bool, Any]:
    """
    Safely acquire, use, and release a resource.

    Args:
        acquire: Function to acquire resource (no args)
        use: Function to use resource (takes resource)
        release: Function to release resource (takes resource)

    Returns:
        Tuple of (success: bool, result_or_error: Any)
    """
    pass
```

**Requirements:**
- Use try-except-finally
- Acquire resource in try block
- Use resource in try block
- Release resource in finally block (must always execute)
- Return (True, result) on success
- Return (False, exception) on failure
- Ensure release is called even if use raises exception
