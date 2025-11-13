# Task: Conditional Filter

Implement a function that filters items based on multiple optional conditions.

**Function signature:**
```python
from typing import Any, Callable, Optional

def conditional_filter(
    items: list,
    min_val: Optional[Callable] = None,
    max_val: Optional[Callable] = None,
    predicate: Optional[Callable] = None
) -> list:
    """
    Filter items based on optional min, max, and custom predicate.

    Args:
        items: List to filter
        min_val: Optional function to extract value for minimum check
        max_val: Optional function to extract value for maximum check
        predicate: Optional additional boolean predicate

    Returns:
        Filtered list
    """
    pass
```

**Requirements:**
- Use lambda functions for flexible filtering
- Apply only the conditions that are not None
- All provided conditions must be satisfied (AND logic)
- If no conditions provided, return all items
- Preserve original order
