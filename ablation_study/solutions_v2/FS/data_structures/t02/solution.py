from collections import OrderedDict


class PriorityLRUCache:
    """
    LRU cache with priority: higher priority items are evicted last.

    Uses OrderedDict per priority level to maintain LRU order within each priority.
    """

    def __init__(self, capacity: int):
        """Initialize cache with given capacity."""
        self.capacity = capacity
        self.cache = {}  # key -> (value, priority)
        self.priority_buckets = {}  # priority -> OrderedDict of keys
        self.evictions = 0

    def get(self, key: str) -> tuple:
        """
        Get value and priority for key.
        Returns (value, priority) or (None, 0) if not found.
        """
        if key not in self.cache:
            return (None, 0)

        value, priority = self.cache[key]
        # Update access time by moving to end of the OrderedDict
        self.priority_buckets[priority].move_to_end(key)
        return (value, priority)

    def put(self, key: str, value, priority: int = 1) -> None:
        """
        Put key-value pair with priority.
        If capacity exceeded, evict lowest priority LRU item.
        """
        if key in self.cache:
            # Remove from old priority bucket
            old_value, old_priority = self.cache[key]
            del self.priority_buckets[old_priority][key]
            if not self.priority_buckets[old_priority]:
                del self.priority_buckets[old_priority]
        elif len(self.cache) >= self.capacity:
            # Need to evict before adding new item
            self._evict()

        # Add to cache
        self.cache[key] = (value, priority)

        # Add to priority bucket (at end for LRU ordering)
        if priority not in self.priority_buckets:
            self.priority_buckets[priority] = OrderedDict()
        self.priority_buckets[priority][key] = True

    def _evict(self) -> None:
        """Evict the lowest priority, least recently used item."""
        # Find lowest priority bucket
        min_priority = min(self.priority_buckets.keys())

        # Get oldest item from that bucket (first item in OrderedDict)
        oldest_key = next(iter(self.priority_buckets[min_priority]))

        # Remove from bucket
        del self.priority_buckets[min_priority][oldest_key]

        # Remove from cache
        del self.cache[oldest_key]

        # Clean up empty bucket
        if not self.priority_buckets[min_priority]:
            del self.priority_buckets[min_priority]

        self.evictions += 1

    def evict_count(self) -> int:
        """Return total number of evictions performed."""
        return self.evictions
