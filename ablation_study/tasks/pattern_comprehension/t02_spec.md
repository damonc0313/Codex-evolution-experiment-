# Task: Dictionary Inversion

Implement a function that inverts a dictionary (swaps keys and values) using comprehensions.

**Function signature:**
```python
def invert_dict(d: dict) -> dict:
    """
    Invert dictionary, swapping keys and values.

    Args:
        d: Dictionary to invert (values must be hashable)

    Returns:
        Inverted dictionary
    """
    pass
```

**Requirements:**
- Use dictionary comprehension
- If multiple keys have the same value, keep the last one
- Handle empty dict
- Values in input become keys in output (must be hashable)
