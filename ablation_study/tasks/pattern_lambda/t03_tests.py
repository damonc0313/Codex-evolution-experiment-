import pytest
from solution import conditional_filter

def test_no_conditions():
    items = [1, 2, 3, 4, 5]
    result = conditional_filter(items)
    assert result == [1, 2, 3, 4, 5]

def test_min_val_only():
    items = [1, 5, 3, 8, 2]
    result = conditional_filter(items, min_val=lambda x: x >= 3)
    assert result == [5, 3, 8]

def test_max_val_only():
    items = [1, 5, 3, 8, 2]
    result = conditional_filter(items, max_val=lambda x: x <= 5)
    assert result == [1, 5, 3, 2]

def test_min_and_max():
    items = [1, 5, 3, 8, 2, 10]
    result = conditional_filter(
        items,
        min_val=lambda x: x >= 3,
        max_val=lambda x: x <= 8
    )
    assert result == [5, 3, 8]

def test_with_predicate():
    items = [1, 2, 3, 4, 5, 6]
    result = conditional_filter(
        items,
        min_val=lambda x: x >= 2,
        predicate=lambda x: x % 2 == 0
    )
    assert result == [2, 4, 6]

def test_all_conditions():
    items = [1, 2, 3, 4, 5, 6, 7, 8]
    result = conditional_filter(
        items,
        min_val=lambda x: x >= 3,
        max_val=lambda x: x <= 7,
        predicate=lambda x: x % 2 == 1
    )
    assert result == [3, 5, 7]

def test_dict_filtering():
    items = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35}
    ]
    result = conditional_filter(
        items,
        min_val=lambda x: x["age"] >= 28,
        predicate=lambda x: "o" in x["name"]
    )
    assert result == [{"name": "Bob", "age": 30}]

def test_empty_input():
    result = conditional_filter([], min_val=lambda x: x > 0)
    assert result == []

def test_no_matches():
    items = [1, 2, 3]
    result = conditional_filter(items, min_val=lambda x: x > 10)
    assert result == []
