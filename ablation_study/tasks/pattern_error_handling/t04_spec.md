# Task: Multi-Exception Handler

Implement a function that calls another function and handles multiple exception types differently.

**Function signature:**
```python
from typing import Callable, Any

def safe_call(
    func: Callable,
    *args,
    on_type_error: Any = "TYPE_ERROR",
    on_value_error: Any = "VALUE_ERROR",
    on_other: Any = "OTHER_ERROR"
) -> Any:
    """
    Call function with args, handling different exceptions.

    Args:
        func: Function to call
        *args: Arguments to pass to function
        on_type_error: Return value for TypeError
        on_value_error: Return value for ValueError
        on_other: Return value for any other exception

    Returns:
        Function result or appropriate error value
    """
    pass
```

**Requirements:**
- Use try-except with multiple except clauses
- Handle TypeError, ValueError, and generic Exception
- Return different values for different exception types
- Pass through successful results unchanged
