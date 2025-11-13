# Task: Cache with Expiration

Implement a SimpleCache class with time-based expiration.

**Class specification:**
```python
import time

class SimpleCache:
    """Simple cache with time-based expiration."""

    def __init__(self, default_ttl: float = 60.0):
        """
        Initialize cache with default time-to-live.

        Args:
            default_ttl: Default expiration time in seconds
        """
        pass

    def set(self, key: str, value: any, ttl: float = None) -> None:
        """
        Set a cache value with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        pass

    def get(self, key: str, default: any = None) -> any:
        """
        Get cached value if not expired.

        Args:
            key: Cache key
            default: Value to return if key missing or expired

        Returns:
            Cached value or default
        """
        pass

    def delete(self, key: str) -> bool:
        """Delete key from cache. Return True if existed."""
        pass

    def clear(self) -> None:
        """Remove all items from cache."""
        pass

    def size(self) -> int:
        """Return number of non-expired items in cache."""
        pass
```

**Requirements:**
- Store value with expiration timestamp
- Automatically remove expired items when accessed
- Use time.time() for timestamps
- TTL parameter overrides default_ttl
