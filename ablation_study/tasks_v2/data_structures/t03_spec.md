# Task: Interval Tree for Overlapping Queries

Implement interval tree supporting overlap queries.

**Class specification:**
```python
class IntervalTree:
    """
    Tree structure for efficient interval overlap queries.
    """

    def __init__(self):
        """Initialize empty interval tree."""
        pass

    def insert(self, start: int, end: int, data: any = None) -> int:
        """
        Insert interval [start, end] with optional data.
        Returns interval ID for later reference.
        """
        pass

    def delete(self, interval_id: int) -> bool:
        """Delete interval by ID. Returns True if existed."""
        pass

    def find_overlapping(self, start: int, end: int) -> list[tuple[int, int, int, any]]:
        """
        Find all intervals overlapping with [start, end].
        Returns list of (interval_id, start, end, data).
        """
        pass
```

**Requirements:**
- insert() is O(log n) amortized
- find_overlapping() is O(log n + k) where k is number of results
- Intervals are closed: [start, end]
- Two intervals overlap if they share any point
- delete() should actually remove from structure

**Example:**
```python
tree = IntervalTree()
id1 = tree.insert(1, 5, "A")
id2 = tree.insert(3, 7, "B")
id3 = tree.insert(10, 15, "C")

tree.find_overlapping(4, 6) == [(id1, 1, 5, "A"), (id2, 3, 7, "B")]
tree.find_overlapping(8, 12) == [(id3, 10, 15, "C")]
tree.delete(id1)
tree.find_overlapping(4, 6) == [(id2, 3, 7, "B")]
```

**Difficulty:** Advanced tree structure with augmentation
