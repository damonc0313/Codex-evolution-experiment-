import pytest
from solution import typed_bin_packing


def test_no_constraints():
    """Basic bin packing without type conflicts."""
    items = [(5, "A"), (3, "A"), (2, "A")]
    capacity = 10
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    # All fit in one bin
    assert len(bins) == 1
    assert set(bins[0]) == {0, 1, 2}


def test_incompatible_types():
    """Types A and B can't share a bin."""
    items = [(5, "A"), (3, "B"), (2, "A")]
    capacity = 10
    incompatible = {("A", "B"), ("B", "A")}
    bins = typed_bin_packing(items, capacity, incompatible)
    # Need at least 2 bins: one for A items, one for B
    assert len(bins) >= 2
    # Verify no bin has both A and B
    for bin_items in bins:
        types = {items[i][1] for i in bin_items}
        if "A" in types:
            assert "B" not in types
        if "B" in types:
            assert "A" not in types


def test_capacity_constraint():
    """Items don't fit due to size."""
    items = [(7, "A"), (6, "A")]
    capacity = 10
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    # Must use 2 bins
    assert len(bins) == 2


def test_single_item():
    """One item in one bin."""
    items = [(5, "A")]
    capacity = 10
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    assert len(bins) == 1
    assert bins[0] == [0]


def test_all_items_packed():
    """Every item appears exactly once."""
    items = [(3, "A"), (4, "B"), (2, "C"), (5, "D")]
    capacity = 10
    incompatible = {("A", "C")}
    bins = typed_bin_packing(items, capacity, incompatible)
    all_items = [item for bin_items in bins for item in bin_items]
    assert sorted(all_items) == [0, 1, 2, 3]


def test_symmetric_incompatibility():
    """(A,B) incompatible implies (B,A) incompatible."""
    items = [(5, "A"), (4, "B"), (3, "A")]
    capacity = 20
    incompatible = {("A", "B")}  # Only one direction
    bins = typed_bin_packing(items, capacity, incompatible)
    # Implementation should treat as symmetric
    for bin_items in bins:
        types = {items[i][1] for i in bin_items}
        # Should not mix A and B
        assert not (("A" in types) and ("B" in types))


def test_bin_size_respected():
    """No bin exceeds capacity."""
    items = [(i, "A") for i in range(1, 11)]
    capacity = 15
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    for bin_items in bins:
        total_size = sum(items[i][0] for i in bin_items)
        assert total_size <= capacity


def test_minimize_bins():
    """Should use reasonable number of bins."""
    items = [(4, "A"), (4, "A"), (4, "A")]
    capacity = 10
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    # Optimal: 2 bins (4+4, 4)
    assert len(bins) <= 2


def test_multiple_incompatibilities():
    """Several incompatible type pairs."""
    items = [(3, "A"), (3, "B"), (3, "C"), (3, "D")]
    capacity = 10
    incompatible = {("A", "B"), ("B", "A"), ("C", "D"), ("D", "C")}
    bins = typed_bin_packing(items, capacity, incompatible)
    # Verify constraints
    for bin_items in bins:
        types = {items[i][1] for i in bin_items}
        for t1, t2 in incompatible:
            if t1 in types:
                assert t2 not in types


def test_same_type_allowed():
    """Multiple items of same type can share bin."""
    items = [(3, "A"), (3, "A"), (3, "A")]
    capacity = 9
    incompatible = set()
    bins = typed_bin_packing(items, capacity, incompatible)
    # All should fit in one bin
    assert len(bins) == 1


def test_complex_constraints():
    """Realistic scenario with multiple types and constraints."""
    items = [
        (5, "hazard"), (3, "food"), (2, "hazard"),
        (4, "food"), (6, "electronics"), (2, "electronics")
    ]
    capacity = 15
    incompatible = {
        ("hazard", "food"), ("food", "hazard"),
        ("hazard", "electronics"), ("electronics", "hazard")
    }
    bins = typed_bin_packing(items, capacity, incompatible)
    # Hazard items must be separate from food and electronics
    for bin_items in bins:
        types = {items[i][1] for i in bin_items}
        if "hazard" in types:
            assert "food" not in types
            assert "electronics" not in types
    # All items packed
    assert sum(len(b) for b in bins) == len(items)
