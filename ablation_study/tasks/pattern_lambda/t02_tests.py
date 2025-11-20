import pytest
from solution import multi_sort

def test_single_criterion():
    items = [{"age": 30}, {"age": 20}, {"age": 25}]
    result = multi_sort(items, ("age", False))
    assert result == [{"age": 20}, {"age": 25}, {"age": 30}]

def test_single_criterion_reverse():
    items = [{"score": 85}, {"score": 95}, {"score": 90}]
    result = multi_sort(items, ("score", True))
    assert result == [{"score": 95}, {"score": 90}, {"score": 85}]

def test_multiple_criteria():
    items = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Alice", "age": 25}
    ]
    result = multi_sort(items, ("name", False), ("age", False))
    assert result == [
        {"name": "Alice", "age": 25},
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]

def test_mixed_reverse():
    items = [
        {"team": "A", "score": 10},
        {"team": "B", "score": 20},
        {"team": "A", "score": 15}
    ]
    result = multi_sort(items, ("team", False), ("score", True))
    assert result == [
        {"team": "A", "score": 15},
        {"team": "A", "score": 10},
        {"team": "B", "score": 20}
    ]

def test_missing_keys():
    items = [
        {"name": "Alice", "age": 30},
        {"name": "Bob"},
        {"name": "Charlie", "age": 25}
    ]
    result = multi_sort(items, ("age", False))
    # Items with age come first, sorted by age; items without age come last
    assert result[0] == {"name": "Charlie", "age": 25}
    assert result[1] == {"name": "Alice", "age": 30}
    assert result[2] == {"name": "Bob"}

def test_empty_list():
    result = multi_sort([], ("key", False))
    assert result == []

def test_original_not_modified():
    items = [{"x": 2}, {"x": 1}]
    original_items = items.copy()
    result = multi_sort(items, ("x", False))
    assert items == original_items
    assert result != items
