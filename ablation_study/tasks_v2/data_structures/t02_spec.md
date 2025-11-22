# Task: LRU Cache with Priority

Implement an LRU cache where items can have priority levels affecting eviction.

**Class specification:**
```python
class PriorityLRUCache:
    """
    LRU cache with priority: higher priority items are evicted last.
    """

    def __init__(self, capacity: int):
        """Initialize cache with given capacity."""
        pass

    def get(self, key: str) -> tuple[any, int]:
        """
        Get value and priority for key.
        Returns (value, priority) or (None, 0) if not found.
        """
        pass

    def put(self, key: str, value: any, priority: int = 1) -> None:
        """
        Put key-value pair with priority.
        If capacity exceeded, evict lowest priority LRU item.
        """
        pass

    def evict_count(self) -> int:
        """Return total number of evictions performed."""
        pass
```

**Requirements:**
- O(1) get and put operations
- When capacity exceeded, evict item with:
  1. Lowest priority first
  2. If tie, least recently used
- Getting an item updates its access time but not priority
- Putting existing key updates value, priority, and access time
- Track eviction count

**Example:**
```python
cache = PriorityLRUCache(2)
cache.put("a", 1, priority=1)
cache.put("b", 2, priority=2)
cache.put("c", 3, priority=1)  # Evicts "a" (priority=1, oldest)
cache.get("b") == (2, 2)
cache.put("d", 4, priority=1)  # Evicts "c" (priority=1, oldest)
cache.evict_count() == 2
```

**Difficulty:** Complex data structure with multiple constraints
