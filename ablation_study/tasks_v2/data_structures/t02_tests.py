import pytest
from solution import PriorityLRUCache


def test_basic_get_put():
    """Simple get and put operations."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1)
    assert cache.get("a") == (1, 1)
    assert cache.get("b") == (None, 0)


def test_capacity_eviction():
    """Evict when capacity exceeded."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1, priority=1)
    cache.put("b", 2, priority=1)
    cache.put("c", 3, priority=1)
    # Should evict "a" (oldest with priority 1)
    assert cache.get("a") == (None, 0)
    assert cache.get("b") == (2, 1)


def test_priority_eviction():
    """Evict lower priority first."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1, priority=1)
    cache.put("b", 2, priority=2)
    cache.put("c", 3, priority=1)
    # Should evict "a" (priority=1), not "b" (priority=2)
    assert cache.get("a") == (None, 0)
    assert cache.get("b") == (2, 2)
    assert cache.get("c") == (3, 1)


def test_lru_within_priority():
    """Within same priority, evict LRU."""
    cache = PriorityLRUCache(3)
    cache.put("a", 1, priority=1)
    cache.put("b", 2, priority=1)
    cache.get("a")  # Access "a", making "b" older
    cache.put("c", 3, priority=1)
    cache.put("d", 4, priority=1)
    # Should evict "b" (oldest with priority 1)
    assert cache.get("b") == (None, 0)
    assert cache.get("a") == (1, 1)


def test_update_existing_key():
    """Putting existing key updates value and priority."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1, priority=1)
    cache.put("a", 10, priority=3)
    assert cache.get("a") == (10, 3)


def test_evict_count():
    """Track number of evictions."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.evict_count() == 0
    cache.put("c", 3)
    assert cache.evict_count() == 1
    cache.put("d", 4)
    assert cache.evict_count() == 2


def test_get_updates_access_time():
    """Get updates LRU but not priority."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1, priority=1)
    cache.put("b", 2, priority=1)
    cache.get("a")  # Access "a"
    cache.put("c", 3, priority=1)
    # Should evict "b", not "a"
    assert cache.get("b") == (None, 0)
    assert cache.get("a") == (1, 1)


def test_default_priority():
    """Default priority is 1."""
    cache = PriorityLRUCache(2)
    cache.put("a", 1)  # No priority specified
    cache.put("b", 2, priority=2)
    cache.put("c", 3)
    # Should evict "a" (priority=1 default)
    assert cache.get("a") == (None, 0)


def test_high_priority_protection():
    """High priority items protected longer."""
    cache = PriorityLRUCache(3)
    cache.put("a", 1, priority=5)
    cache.put("b", 2, priority=1)
    cache.put("c", 3, priority=1)
    cache.put("d", 4, priority=1)
    # Should evict "b" (oldest priority 1), not "a" (priority 5)
    assert cache.get("a") == (1, 5)
    assert cache.get("b") == (None, 0)


def test_single_capacity():
    """Cache with capacity 1."""
    cache = PriorityLRUCache(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == (None, 0)
    assert cache.get("b") == (2, 1)
    assert cache.evict_count() == 1


def test_complex_scenario():
    """Multiple operations with mixed priorities."""
    cache = PriorityLRUCache(3)
    cache.put("a", 1, priority=2)
    cache.put("b", 2, priority=1)
    cache.put("c", 3, priority=3)
    cache.get("b")  # Access low priority
    cache.put("d", 4, priority=1)  # Should evict oldest priority 1
    assert cache.get("b") == (None, 0)  # "b" accessed but lowest priority
    cache.put("e", 5, priority=1)  # Should evict "d"
    assert cache.get("a") == (1, 2)  # Higher priority survives
    assert cache.get("c") == (3, 3)  # Highest priority survives
