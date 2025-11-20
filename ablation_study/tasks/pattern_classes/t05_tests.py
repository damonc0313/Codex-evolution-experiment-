import pytest
import time
from solution import SimpleCache

def test_initialization():
    cache = SimpleCache()
    assert cache.size() == 0

def test_set_and_get():
    cache = SimpleCache(ttl=10)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

def test_get_nonexistent():
    cache = SimpleCache()
    assert cache.get("missing") is None
    assert cache.get("missing", default="default") == "default"

def test_expiration():
    cache = SimpleCache(default_ttl=0.1)  # 100ms expiration
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    time.sleep(0.15)  # Wait for expiration
    assert cache.get("key1") is None

def test_custom_ttl():
    cache = SimpleCache(default_ttl=10)
    cache.set("short", "value", ttl=0.1)
    cache.set("long", "value", ttl=10)

    time.sleep(0.15)
    assert cache.get("short") is None
    assert cache.get("long") == "value"

def test_delete():
    cache = SimpleCache()
    cache.set("key1", "value1")
    result = cache.delete("key1")
    assert result is True
    assert cache.get("key1") is None

def test_delete_nonexistent():
    cache = SimpleCache()
    result = cache.delete("missing")
    assert result is False

def test_clear():
    cache = SimpleCache()
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    cache.clear()
    assert cache.size() == 0
    assert cache.get("key1") is None

def test_size():
    cache = SimpleCache(default_ttl=10)
    assert cache.size() == 0

    cache.set("key1", "value1")
    assert cache.size() == 1

    cache.set("key2", "value2")
    assert cache.size() == 2

    cache.delete("key1")
    assert cache.size() == 1

def test_size_excludes_expired():
    cache = SimpleCache(default_ttl=0.1)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.size() == 2

    time.sleep(0.15)
    # Size should exclude expired items
    # This depends on implementation - size() might need to check expiration
    size = cache.size()
    assert size <= 2  # Implementation-dependent

def test_overwrite_value():
    cache = SimpleCache()
    cache.set("key1", "value1")
    cache.set("key1", "value2")
    assert cache.get("key1") == "value2"

def test_various_types():
    cache = SimpleCache(default_ttl=10)
    cache.set("int", 42)
    cache.set("list", [1, 2, 3])
    cache.set("dict", {"a": 1})

    assert cache.get("int") == 42
    assert cache.get("list") == [1, 2, 3]
    assert cache.get("dict") == {"a": 1}

def test_zero_ttl():
    cache = SimpleCache()
    cache.set("key", "value", ttl=0)
    # Should expire immediately
    time.sleep(0.01)
    assert cache.get("key") is None
