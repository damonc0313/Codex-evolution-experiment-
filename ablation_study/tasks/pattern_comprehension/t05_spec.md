# Task: Grouped Statistics

Implement a function that groups items and computes statistics using comprehensions.

**Function signature:**
```python
def group_stats(items: list[dict], group_key: str, value_key: str) -> dict[str, dict]:
    """
    Group items by a key and compute statistics on values.

    Args:
        items: List of dictionaries
        group_key: Key to group by
        value_key: Key to compute statistics on

    Returns:
        Dict mapping group names to {"count": int, "sum": num, "avg": float}
    """
    pass
```

**Requirements:**
- Use dictionary and list comprehensions
- Group items by group_key
- For each group, compute count, sum, and average of value_key
- Handle empty input
- Handle missing keys gracefully (skip those items)
