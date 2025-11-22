import pytest
from solution import pattern_cycle


def test_simple_cycle():
    """Basic cycle matching pattern."""
    graph = {0: [1], 1: [2], 2: [0]}
    values = {0: "A", 1: "B", 2: "C"}
    result = pattern_cycle(graph, values, ["A", "B", "C"])
    assert set(result) == {0, 1, 2}


def test_pattern_wraps():
    """Pattern wraps around cycle."""
    graph = {0: [1], 1: [2], 2: [0]}
    values = {0: "A", 1: "B", 2: "C"}
    result = pattern_cycle(graph, values, ["B", "C", "A"])
    # Should find cycle starting at 1
    assert result in ([1, 2, 0], [1, 2, 0, 1])


def test_no_cycle():
    """Graph has no cycles."""
    graph = {0: [1], 1: [2], 2: []}
    values = {0: "A", 1: "B", 2: "C"}
    result = pattern_cycle(graph, values, ["A", "B"])
    assert result == []


def test_pattern_not_in_cycle():
    """Cycle exists but doesn't match pattern."""
    graph = {0: [1], 1: [0]}
    values = {0: "A", 1: "B"}
    result = pattern_cycle(graph, values, ["X", "Y"])
    assert result == []


def test_multiple_cycles():
    """Graph has multiple cycles - find any matching."""
    graph = {
        0: [1], 1: [0],  # Cycle: A-B
        2: [3], 3: [2]   # Cycle: C-D
    }
    values = {0: "A", 1: "B", 2: "C", 3: "D"}
    result = pattern_cycle(graph, values, ["C", "D"])
    assert set(result) == {2, 3}


def test_self_loop():
    """Self-loop is a cycle."""
    graph = {0: [0]}
    values = {0: "A"}
    result = pattern_cycle(graph, values, ["A"])
    assert result == [0]


def test_complex_graph():
    """More complex graph structure."""
    graph = {0: [1], 1: [2], 2: [0, 3], 3: [1]}
    values = {0: "A", 1: "B", 2: "C", 3: "D"}
    # Cycle 1-2-3-1 matches "B","C","D"
    result = pattern_cycle(graph, values, ["B", "C", "D"])
    assert len(result) >= 3
