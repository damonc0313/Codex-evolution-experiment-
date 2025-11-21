# Task: Disjoint Set Union with Rollback

Implement Union-Find with ability to rollback operations.

**Class specification:**
```python
class RollbackDSU:
    """
    Disjoint Set Union with operation history and rollback.
    """

    def __init__(self, n: int):
        """Initialize with n elements (0 to n-1)."""
        pass

    def union(self, x: int, y: int) -> bool:
        """
        Union sets containing x and y.
        Returns True if they were in different sets.
        """
        pass

    def find(self, x: int) -> int:
        """Find root of set containing x."""
        pass

    def checkpoint(self) -> int:
        """
        Create checkpoint of current state.
        Returns checkpoint ID.
        """
        pass

    def rollback(self, checkpoint_id: int) -> None:
        """Rollback to specified checkpoint state."""
        pass

    def count_sets(self) -> int:
        """Return number of disjoint sets."""
        pass
```

**Requirements:**
- find() must be O(log n) or better
- union() must be O(log n) or better
- rollback() must restore exact state at checkpoint
- Can rollback multiple times to same or different checkpoints
- Multiple checkpoints can exist simultaneously

**Example:**
```python
dsu = RollbackDSU(5)  # {0}, {1}, {2}, {3}, {4}
dsu.union(0, 1)       # {0,1}, {2}, {3}, {4}
cp1 = dsu.checkpoint()
dsu.union(2, 3)       # {0,1}, {2,3}, {4}
dsu.union(0, 2)       # {0,1,2,3}, {4}
assert dsu.count_sets() == 2

dsu.rollback(cp1)
assert dsu.count_sets() == 4  # Back to {0,1}, {2}, {3}, {4}
```

**Difficulty:** DSU with state management
