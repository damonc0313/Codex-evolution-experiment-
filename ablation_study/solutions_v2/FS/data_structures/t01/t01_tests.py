import pytest
from solution import RangeQueryTree


def test_basic_range_sum():
    """Simple range sum query."""
    tree = RangeQueryTree([1, 3, 5, 7, 9, 11])
    assert tree.range_sum(1, 3) == 15  # 3 + 5 + 7


def test_single_element_range():
    """Range with single element."""
    tree = RangeQueryTree([1, 3, 5, 7, 9])
    assert tree.range_sum(2, 2) == 5
    assert tree.range_max(2, 2) == 5


def test_full_range():
    """Query entire array."""
    tree = RangeQueryTree([1, 2, 3, 4, 5])
    assert tree.range_sum(0, 4) == 15
    assert tree.range_max(0, 4) == 5


def test_update_affects_sum():
    """Update changes subsequent queries."""
    tree = RangeQueryTree([1, 3, 5, 7, 9, 11])
    assert tree.range_sum(1, 3) == 15
    tree.update(2, 10)
    assert tree.range_sum(1, 3) == 20  # 3 + 10 + 7


def test_update_affects_max():
    """Update changes max query."""
    tree = RangeQueryTree([1, 3, 5, 7, 9])
    assert tree.range_max(0, 4) == 9
    tree.update(2, 20)
    assert tree.range_max(0, 4) == 20


def test_multiple_updates():
    """Several updates in sequence."""
    tree = RangeQueryTree([1, 2, 3, 4, 5])
    tree.update(0, 10)
    tree.update(4, 50)
    assert tree.range_sum(0, 4) == 69  # 10+2+3+4+50


def test_negative_values():
    """Handle negative numbers."""
    tree = RangeQueryTree([-5, 3, -2, 7, -1])
    assert tree.range_sum(0, 4) == 2
    assert tree.range_max(0, 2) == 3


def test_boundary_indices():
    """First and last elements."""
    tree = RangeQueryTree([10, 20, 30, 40, 50])
    assert tree.range_sum(0, 0) == 10
    assert tree.range_sum(4, 4) == 50
    assert tree.range_max(0, 0) == 10
    assert tree.range_max(4, 4) == 50


def test_overlapping_queries():
    """Multiple queries on overlapping ranges."""
    tree = RangeQueryTree([1, 2, 3, 4, 5])
    assert tree.range_sum(0, 2) == 6
    assert tree.range_sum(2, 4) == 12
    assert tree.range_sum(1, 3) == 9


def test_large_array():
    """Performance on larger array."""
    arr = list(range(1000))
    tree = RangeQueryTree(arr)
    # Sum of 0..999 = 999*1000/2 = 499500
    assert tree.range_sum(0, 999) == 499500
    tree.update(500, 10000)
    assert tree.range_sum(500, 500) == 10000


def test_all_same_values():
    """Array with identical values."""
    tree = RangeQueryTree([7, 7, 7, 7, 7])
    assert tree.range_sum(1, 3) == 21
    assert tree.range_max(0, 4) == 7
