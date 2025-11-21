# Task: Range Query Tree with Updates

Implement a data structure supporting range sum queries and point updates.

**Class specification:**
```python
class RangeQueryTree:
    """
    Data structure for efficient range sum queries and point updates.
    """

    def __init__(self, arr: list[int]):
        """Initialize with array."""
        pass

    def update(self, index: int, value: int) -> None:
        """Set arr[index] = value."""
        pass

    def range_sum(self, left: int, right: int) -> int:
        """Return sum of arr[left:right+1] (inclusive)."""
        pass

    def range_max(self, left: int, right: int) -> int:
        """Return max of arr[left:right+1] (inclusive)."""
        pass
```

**Requirements:**
- Use segment tree, Fenwick tree, or similar efficient structure
- update() must be O(log n) or better
- range_sum() must be O(log n) or better
- range_max() must be O(log n) or better
- Handle edge cases (single element, empty range)
- Indices are 0-based

**Example:**
```python
tree = RangeQueryTree([1, 3, 5, 7, 9, 11])
tree.range_sum(1, 3) == 15  # 3 + 5 + 7
tree.update(2, 10)  # arr becomes [1, 3, 10, 7, 9, 11]
tree.range_sum(1, 3) == 20  # 3 + 10 + 7
tree.range_max(0, 5) == 11
```

**Difficulty:** Advanced data structure implementation
