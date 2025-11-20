# Task: Batch Process Until Empty

Implement a function that processes items in batches from a list, removing processed items until the list is empty.

**Function signature:**
```python
def batch_process(items: list, batch_size: int = 3) -> list[list]:
    """
    Process items in batches, returning list of batches.

    Args:
        items: List of items to process (will be mutated)
        batch_size: Number of items per batch

    Returns:
        List of batches (each batch is a list)
    """
    pass
```

**Requirements:**
- Use walrus operator in a while loop to extract batches
- Remove processed items from the input list (mutate it)
- Handle final batch that may be smaller than batch_size
- Handle empty input list
- Preserve item order within batches
