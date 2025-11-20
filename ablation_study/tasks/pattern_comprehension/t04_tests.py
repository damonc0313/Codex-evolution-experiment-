import pytest
from solution import build_dict

def test_no_condition():
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    result = build_dict(keys, values)
    assert result == {"a": 1, "b": 2, "c": 3}

def test_with_condition():
    keys = ["a", "b", "c", "d"]
    values = [1, 2, 3, 4]
    result = build_dict(keys, values, lambda k, v: v % 2 == 0)
    assert result == {"b": 2, "d": 4}

def test_key_based_condition():
    keys = ["apple", "banana", "apricot", "berry"]
    values = [1, 2, 3, 4]
    result = build_dict(keys, values, lambda k, v: k.startswith("a"))
    assert result == {"apple": 1, "apricot": 3}

def test_combined_condition():
    keys = range(10)
    values = range(10, 20)
    result = build_dict(
        list(keys),
        list(values),
        lambda k, v: k > 5 and v < 18
    )
    assert result == {6: 16, 7: 17}

def test_empty_lists():
    result = build_dict([], [])
    assert result == {}

def test_all_filtered_out():
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    result = build_dict(keys, values, lambda k, v: False)
    assert result == {}

def test_none_condition():
    keys = [1, 2, 3]
    values = ["one", "two", "three"]
    result = build_dict(keys, values, None)
    assert result == {1: "one", 2: "two", 3: "three"}

def test_complex_values():
    keys = ["a", "b", "c"]
    values = [[1, 2], [3, 4], [5, 6]]
    result = build_dict(keys, values, lambda k, v: sum(v) > 5)
    assert result == {"b": [3, 4], "c": [5, 6]}
