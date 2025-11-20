import pytest
from solution import flatten

def test_all_lists():
    nested = [[1, 2], [3, 4], [5, 6]]
    assert flatten(nested) == [1, 2, 3, 4, 5, 6]

def test_mixed_items():
    nested = [[1, 2], 3, [4, 5], 6]
    assert flatten(nested) == [1, 2, 3, 4, 5, 6]

def test_empty_sublists():
    nested = [[1], [], [2, 3], [], [4]]
    assert flatten(nested) == [1, 2, 3, 4]

def test_empty_input():
    assert flatten([]) == []

def test_single_items_only():
    nested = [1, 2, 3, 4]
    assert flatten(nested) == [1, 2, 3, 4]

def test_strings():
    nested = [["hello"], "world", ["foo", "bar"]]
    assert flatten(nested) == ["hello", "world", "foo", "bar"]

def test_one_level_only():
    # Should not recursively flatten
    nested = [[1, [2, 3]], 4, [5, [6]]]
    result = flatten(nested)
    assert result == [1, [2, 3], 4, 5, [6]]

def test_large_sublists():
    nested = [[i for i in range(100)], [i for i in range(100, 200)]]
    result = flatten(nested)
    assert len(result) == 200
    assert result[0] == 0
    assert result[-1] == 199
