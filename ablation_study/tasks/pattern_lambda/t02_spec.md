# Task: Custom Sorter

Implement a function that sorts items by multiple criteria using lambda-based key functions.

**Function signature:**
```python
from typing import Any, Callable

def multi_sort(items: list[dict], *criteria: tuple[str, bool]) -> list[dict]:
    """
    Sort items by multiple criteria.

    Args:
        items: List of dictionaries to sort
        *criteria: Tuples of (key_name, reverse) for sorting priority

    Returns:
        Sorted list (original list is not modified)
    """
    pass
```

**Requirements:**
- Use lambda functions to create sort keys
- First criterion is primary sort, subsequent are tiebreakers
- Each criterion is (key_name, reverse_bool)
- Handle missing keys gracefully (treat as None, sort to end)
- Return new list, don't modify original
