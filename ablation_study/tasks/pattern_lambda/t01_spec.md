# Task: Transform Pipeline

Implement a function that applies a sequence of transformations to data using lambda functions.

**Function signature:**
```python
from typing import Callable, Any

def transform_pipeline(data: list, *transforms: Callable) -> list:
    """
    Apply a sequence of transformations to each item in data.

    Args:
        data: List of items to transform
        *transforms: Variable number of transformation functions

    Returns:
        List with all transformations applied in sequence
    """
    pass
```

**Requirements:**
- Use lambda functions and functional composition
- Apply transforms left-to-right for each item
- Handle empty data and empty transforms
- Each transform takes one argument and returns one value
