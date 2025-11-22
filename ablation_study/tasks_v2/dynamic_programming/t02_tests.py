import pytest
from solution import dependent_knapsack


def test_no_dependencies():
    """Standard knapsack without dependencies."""
    items = [
        {"weight": 2, "value": 10, "requires": []},
        {"weight": 3, "value": 15, "requires": []},
        {"weight": 1, "value": 5, "requires": []}
    ]
    value, selected = dependent_knapsack(5, items)
    assert value == 20  # Items 0 and 2
    assert set(selected) == {0, 2}


def test_simple_dependency():
    """Item requires another item."""
    items = [
        {"weight": 2, "value": 10, "requires": []},
        {"weight": 3, "value": 15, "requires": [0]},
        {"weight": 1, "value": 5, "requires": []}
    ]
    value, selected = dependent_knapsack(6, items)
    assert value == 30  # All items
    assert set(selected) == {0, 1, 2}


def test_dependency_chain():
    """Transitive dependencies."""
    items = [
        {"weight": 1, "value": 5, "requires": []},
        {"weight": 2, "value": 10, "requires": [0]},
        {"weight": 3, "value": 20, "requires": [1]}
    ]
    value, selected = dependent_knapsack(6, items)
    assert value == 35  # Must take all due to chain
    assert selected == [0, 1, 2]


def test_cannot_afford_dependencies():
    """Dependency makes item unselectable."""
    items = [
        {"weight": 10, "value": 50, "requires": []},
        {"weight": 2, "value": 100, "requires": [0]}
    ]
    value, selected = dependent_knapsack(5, items)
    assert value == 0  # Can't take item 1 without 0, and 0 doesn't fit
    assert selected == []


def test_empty_items():
    """No items."""
    assert dependent_knapsack(10, []) == (0, [])


def test_zero_capacity():
    """No capacity."""
    items = [{"weight": 1, "value": 10, "requires": []}]
    assert dependent_knapsack(0, items) == (0, [])


def test_multiple_dependencies():
    """Item requires multiple items."""
    items = [
        {"weight": 1, "value": 5, "requires": []},
        {"weight": 1, "value": 6, "requires": []},
        {"weight": 2, "value": 20, "requires": [0, 1]}
    ]
    value, selected = dependent_knapsack(4, items)
    assert value == 31  # All items
    assert set(selected) == {0, 1, 2}


def test_optimal_selection_with_deps():
    """Choose best combination considering deps."""
    items = [
        {"weight": 3, "value": 10, "requires": []},
        {"weight": 2, "value": 8, "requires": []},
        {"weight": 4, "value": 25, "requires": [0]}
    ]
    value, selected = dependent_knapsack(7, items)
    assert value == 35  # Items 0 and 2 (need 0 for 2)
    assert set(selected) == {0, 2}


def test_sorted_output():
    """Indices returned in sorted order."""
    items = [
        {"weight": 1, "value": 5, "requires": []},
        {"weight": 1, "value": 6, "requires": []},
        {"weight": 1, "value": 7, "requires": []}
    ]
    _, selected = dependent_knapsack(3, items)
    assert selected == sorted(selected)
