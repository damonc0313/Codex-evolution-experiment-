# Task: Reducer with Custom Operations

Implement a function that reduces a list using custom binary operations.

**Function signature:**
```python
from typing import Any, Callable
from functools import reduce

def custom_reduce(items: list, operation: str, initial: Any = None) -> Any:
    """
    Reduce list using specified operation.

    Args:
        items: List to reduce
        operation: Operation name ("sum", "product", "concat", "min", "max", "and", "or")
        initial: Initial value (uses sensible default if None)

    Returns:
        Reduced value
    """
    pass
```

**Requirements:**
- Use functools.reduce with lambda functions
- Support operations: sum, product, concat, min, max, and, or
- Use appropriate initial values when not provided
- Handle empty lists appropriately
- Raise ValueError for unknown operations
