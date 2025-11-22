import pytest
from solution import json_query


def test_simple_key():
    """Access top-level key."""
    data = {"name": "Alice", "age": 30}
    assert json_query(data, "name") == ["Alice"]
    assert json_query(data, "age") == [30]


def test_nested_keys():
    """Access nested objects."""
    data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
    assert json_query(data, "user.name") == ["Alice"]
    assert json_query(data, "user.address.city") == ["NYC"]


def test_array_index():
    """Access array element by index."""
    data = {"items": [10, 20, 30, 40]}
    assert json_query(data, "items[0]") == [10]
    assert json_query(data, "items[2]") == [30]


def test_array_wildcard():
    """Access all array elements."""
    data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert json_query(data, "users[*].name") == ["Alice", "Bob"]


def test_missing_key():
    """Missing key returns empty list."""
    data = {"name": "Alice"}
    assert json_query(data, "age") == []
    assert json_query(data, "user.name") == []


def test_missing_array_index():
    """Out of bounds index returns empty list."""
    data = {"items": [1, 2, 3]}
    assert json_query(data, "items[10]") == []


def test_complex_path():
    """Combination of nested objects and arrays."""
    data = {
        "store": {
            "books": [
                {"title": "Book1", "authors": ["A1", "A2"]},
                {"title": "Book2", "authors": ["B1"]}
            ]
        }
    }
    assert json_query(data, "store.books[0].title") == ["Book1"]
    assert json_query(data, "store.books[*].title") == ["Book1", "Book2"]
    assert json_query(data, "store.books[0].authors[1]") == ["A2"]


def test_wildcard_with_index():
    """Wildcard followed by specific index."""
    data = {
        "users": [
            {"emails": ["a1@x.com", "a2@x.com"]},
            {"emails": ["b1@x.com", "b2@x.com"]}
        ]
    }
    result = json_query(data, "users[*].emails[0]")
    assert result == ["a1@x.com", "b1@x.com"]


def test_empty_path():
    """Empty or root path."""
    data = {"name": "Alice"}
    # Implementation specific - might return [data] or []
    result = json_query(data, "")
    assert isinstance(result, list)


def test_array_of_primitives():
    """Array containing primitive values."""
    data = {"numbers": [1, 2, 3, 4, 5]}
    assert json_query(data, "numbers[*]") == [1, 2, 3, 4, 5]


def test_missing_nested_path():
    """Partial path exists but full path doesn't."""
    data = {"user": {"name": "Alice"}}
    assert json_query(data, "user.address.city") == []


def test_null_values():
    """Handle null/None values in data."""
    data = {"user": {"name": None}}
    assert json_query(data, "user.name") == [None]


def test_negative_index():
    """Negative array indices (optional)."""
    data = {"items": [1, 2, 3]}
    # May or may not support negative indexing
    result = json_query(data, "items[-1]")
    assert result == [3] or result == []
