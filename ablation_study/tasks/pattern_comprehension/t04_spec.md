# Task: Conditional Dictionary Builder

Implement a function that builds a dictionary from two lists with conditional inclusion.

**Function signature:**
```python
from typing import Callable, Optional

def build_dict(
    keys: list,
    values: list,
    condition: Optional[Callable[[any, any], bool]] = None
) -> dict:
    """
    Build dictionary from keys and values, optionally filtering pairs.

    Args:
        keys: List of keys
        values: List of values (same length as keys)
        condition: Optional function(key, value) -> bool to filter pairs

    Returns:
        Dictionary with filtered key-value pairs
    """
    pass
```

**Requirements:**
- Use dictionary comprehension with zip
- Apply condition if provided
- Handle empty lists
- Handle None condition (include all pairs)
- Keys and values lists must be same length
