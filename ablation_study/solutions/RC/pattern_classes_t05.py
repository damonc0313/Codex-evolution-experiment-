import time

class SimpleCache:
    """
    Simple cache with time-based expiration.

    """

    def __init__(self, default_ttl: float = 60.0):
        """
        Initialize cache with default time-to-live.

        Args:
            default_ttl: Default expiration time in seconds
        """
        self._default_ttl = default_ttl
        self._cache = {}  # {key: (value, expiration_timestamp)}

    def set(self, key: str, value: any, ttl: float = None) -> None:
        """
        Set a cache value with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self._default_ttl

        expiration = time.time() + ttl
        self._cache[key] = (value, expiration)

    def get(self, key: str, default: any = None) -> any:
        """
        Get cached value if not expired.

        Args:
            key: Cache key
            default: Value to return if key missing or expired

        Returns:
            Cached value or default
        """
        if key not in self._cache:
            return default

        value, expiration = self._cache[key]

        # Check if expired
        if time.time() > expiration:
            # Lazy cleanup
            del self._cache[key]
            return default

        return value

    def delete(self, key: str) -> bool:
        """Delete key from cache. Return True if existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Remove all items from cache."""
        self._cache.clear()

    def size(self) -> int:
        """Return number of non-expired items in cache."""
        # Clean expired items first
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiration) in self._cache.items()
            if current_time > expiration
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(self._cache)
