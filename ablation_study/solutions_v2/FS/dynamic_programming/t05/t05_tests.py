import pytest
from solution import balanced_partition


def test_simple_partition():
    """Basic 3-way equal sum partition."""
    arr = [1, 2, 3, 4, 5, 6]  # sum = 21, each subset = 7
    result = balanced_partition(arr, 3)
    assert len(result) == 3
    # Verify each subset sums to 7
    for subset in result:
        total = sum(arr[i] for i in subset)
        assert total == 7


def test_impossible_partition():
    """Sum not divisible by k."""
    arr = [1, 2, 3]
    result = balanced_partition(arr, 2)
    assert result == []


def test_single_subset():
    """k=1, return all elements."""
    arr = [1, 2, 3, 4]
    result = balanced_partition(arr, 1)
    assert len(result) == 1
    assert set(result[0]) == {0, 1, 2, 3}


def test_cannot_achieve_equal_sum():
    """Sum divisible but can't partition."""
    arr = [1, 1, 1, 3]  # sum = 6, need 2 subsets of 3 each
    result = balanced_partition(arr, 2)
    # Can't make two subsets of sum 3
    assert result == []


def test_balanced_sizes():
    """Minimize max subset size."""
    arr = [1, 1, 1, 1, 1, 1]  # sum = 6
    result = balanced_partition(arr, 2)
    # Each subset should have 3 elements (sum=3)
    assert len(result) == 2
    assert all(len(subset) == 3 for subset in result)


def test_empty_array():
    """No elements."""
    result = balanced_partition([], 1)
    assert result == [[]]


def test_two_way_partition():
    """Classic 2-subset partition."""
    arr = [1, 5, 11, 5]  # sum = 22, each = 11
    result = balanced_partition(arr, 2)
    assert len(result) == 2
    sums = [sum(arr[i] for i in subset) for subset in result]
    assert all(s == 11 for s in sums)
