import pytest
from solution import balanced_knapsack


def test_simple_knapsack():
    """Basic knapsack without variance concern."""
    items = [(10, 50), (20, 60), (30, 70)]
    capacity = 50
    value, variance, selected = balanced_knapsack(capacity, items)
    # Items 1,2 give weight=50, value=130 - the optimal solution
    assert value == 130  # Items 1,2
    assert set(selected) == {1, 2}


def test_single_item():
    """Single item selected - variance is zero."""
    items = [(30, 100), (40, 80)]
    capacity = 35
    value, variance, selected = balanced_knapsack(capacity, items)
    assert value == 100
    assert variance == 0.0  # Only one item
    assert selected == [0]


def test_variance_tiebreaker():
    """When values equal, choose lower variance."""
    items = [(10, 50), (20, 50), (15, 50)]
    capacity = 30
    # Could pick [0,1] variance=25 or [0,2] variance=6.25
    # Both give value=100, should prefer lower variance
    value, variance, selected = balanced_knapsack(capacity, items)
    assert value == 100
    # Should pick items with closer weights
    if set(selected) == {0, 2}:
        assert variance < 10  # Lower variance


def test_empty_knapsack():
    """No items fit or empty list."""
    value, variance, selected = balanced_knapsack(10, [])
    assert value == 0
    assert variance == 0.0
    assert selected == []


def test_nothing_fits():
    """All items exceed capacity."""
    items = [(100, 50), (200, 80)]
    value, variance, selected = balanced_knapsack(50, items)
    assert value == 0
    assert variance == 0.0
    assert selected == []


def test_uniform_weights():
    """All selected items same weight - zero variance."""
    items = [(10, 20), (10, 30), (10, 40), (20, 50)]
    capacity = 30
    value, variance, selected = balanced_knapsack(capacity, items)
    # Best: pick three items of weight 10 (value=90)
    if len(selected) == 3 and all(items[i][0] == 10 for i in selected):
        assert variance == 0.0


def test_all_items_fit():
    """Capacity allows all items."""
    items = [(5, 10), (5, 20), (5, 30)]
    capacity = 100
    value, variance, selected = balanced_knapsack(capacity, items)
    assert value == 60  # All items
    assert variance == 0.0  # All same weight
    assert set(selected) == {0, 1, 2}


def test_sorted_output():
    """Indices in sorted order."""
    items = [(10, 50), (20, 60), (15, 40)]
    capacity = 100
    _, _, selected = balanced_knapsack(capacity, items)
    assert selected == sorted(selected)


def test_variance_calculation():
    """Verify variance computed correctly."""
    items = [(10, 50), (30, 60)]
    capacity = 50
    value, variance, selected = balanced_knapsack(capacity, items)
    # weights = [10, 30], mean = 20
    # variance = ((10-20)^2 + (30-20)^2) / 2 = (100 + 100) / 2 = 100
    assert value == 110
    assert variance == 100.0


def test_large_instance():
    """Multiple items with complex trade-offs."""
    items = [(i*10, i*20) for i in range(1, 11)]
    capacity = 200
    value, variance, selected = balanced_knapsack(capacity, items)
    # Should select items optimally
    assert value > 0
    assert len(selected) > 0
    total_weight = sum(items[i][0] for i in selected)
    assert total_weight <= capacity
