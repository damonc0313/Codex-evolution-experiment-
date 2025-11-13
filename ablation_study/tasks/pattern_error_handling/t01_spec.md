# Task: Safe Division

Implement a function that safely divides two numbers with proper error handling.

**Function signature:**
```python
from typing import Optional

def safe_divide(a: float, b: float, default: Optional[float] = None) -> Optional[float]:
    """
    Safely divide a by b, handling division by zero.

    Args:
        a: Numerator
        b: Denominator
        default: Value to return on error (None if not provided)

    Returns:
        Result of division, or default on error
    """
    pass
```

**Requirements:**
- Use try-except for ZeroDivisionError
- Return default value on division by zero
- Handle type errors gracefully (return default)
- Return None if default not provided and error occurs
