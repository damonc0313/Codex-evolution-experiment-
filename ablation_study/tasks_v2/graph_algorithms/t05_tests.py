import pytest
from solution import weighted_matching


def test_perfect_matching():
    """All nodes matched."""
    left = ["A1", "A2"]
    right = ["B1", "B2"]
    edges = {
        ("A1", "B1"): 10, ("A1", "B2"): 5,
        ("A2", "B1"): 3, ("A2", "B2"): 8
    }
    size, matching = weighted_matching(left, right, edges)
    assert size == 2
    # Best total score: A1->B1 (10) + A2->B2 (8) = 18
    assert matching == {"A1": "B1", "A2": "B2"}


def test_imperfect_matching():
    """Not all nodes can be matched."""
    left = ["A1", "A2", "A3"]
    right = ["B1", "B2"]
    edges = {
        ("A1", "B1"): 5, ("A2", "B2"): 3
    }
    size, matching = weighted_matching(left, right, edges)
    assert size == 2  # Max cardinality
    assert len(matching) == 2


def test_no_edges():
    """No possible matching."""
    left = ["A1"]
    right = ["B1"]
    edges = {}
    size, matching = weighted_matching(left, right, edges)
    assert size == 0
    assert matching == {}


def test_preference_tie_breaking():
    """Multiple max-cardinality matchings, pick highest score."""
    left = ["A1"]
    right = ["B1", "B2"]
    edges = {
        ("A1", "B1"): 10,
        ("A1", "B2"): 5
    }
    size, matching = weighted_matching(left, right, edges)
    assert matching["A1"] == "B1"  # Higher preference


def test_single_edge():
    """Trivial single match."""
    left = ["A"]
    right = ["B"]
    edges = {("A", "B"): 1}
    size, matching = weighted_matching(left, right, edges)
    assert size == 1
    assert matching == {"A": "B"}


def test_empty_partitions():
    """No nodes."""
    size, matching = weighted_matching([], [], {})
    assert size == 0
    assert matching == {}
