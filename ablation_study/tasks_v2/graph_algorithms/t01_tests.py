import pytest
from solution import path_avoiding_pairs


def test_simple_path_no_forbidden():
    """Basic shortest path."""
    graph = {
        0: [(1, 5), (2, 10)],
        1: [(2, 3)],
        2: []
    }
    dist, path = path_avoiding_pairs(graph, 0, 2, set())
    assert dist == 8
    assert path == [0, 1, 2]


def test_forbidden_pair_forces_detour():
    """Must avoid forbidden edge pair."""
    graph = {
        0: [(1, 5), (2, 10)],
        1: [(2, 3), (3, 20)],
        2: [(3, 2)],
        3: []
    }
    dist, path = path_avoiding_pairs(graph, 0, 3, {(2, 3)})
    # Can't go 0->1->2->3 because (2,3) forbidden
    # Must go 0->1->3
    assert dist == 25
    assert path == [0, 1, 3]


def test_no_valid_path():
    """All paths blocked by forbidden pairs."""
    graph = {
        0: [(1, 1)],
        1: [(2, 1)],
        2: []
    }
    dist, path = path_avoiding_pairs(graph, 0, 2, {(1, 2)})
    assert dist == -1
    assert path == []


def test_disconnected_graph():
    """No path exists."""
    graph = {
        0: [(1, 5)],
        1: [],
        2: []
    }
    dist, path = path_avoiding_pairs(graph, 0, 2, set())
    assert dist == -1
    assert path == []


def test_single_node_path():
    """Start equals end."""
    graph = {0: [(1, 5)], 1: []}
    dist, path = path_avoiding_pairs(graph, 0, 0, set())
    assert dist == 0
    assert path == [0]


def test_multiple_forbidden_pairs():
    """Several forbidden transitions."""
    graph = {
        0: [(1, 1), (2, 10)],
        1: [(3, 1)],
        2: [(3, 1)],
        3: []
    }
    forbidden = {(1, 3), (0, 2)}
    dist, path = path_avoiding_pairs(graph, 0, 3, forbidden)
    # Can't do 0->1->3 (forbidden)
    # Can't do 0->2 at all (forbidden)
    # No valid path
    assert dist == -1


def test_self_loop():
    """Graph with self-loop."""
    graph = {
        0: [(0, 1), (1, 5)],
        1: []
    }
    dist, path = path_avoiding_pairs(graph, 0, 1, set())
    assert dist == 5
    assert path == [0, 1]


def test_bidirectional_forbidden():
    """Forbidden pair is directional."""
    graph = {
        0: [(1, 5)],
        1: [(2, 5)],
        2: [(1, 5)]
    }
    # Forbidden (1,2) means can't go FROM 1 TO 2
    # But can go FROM 2 TO 1
    dist, path = path_avoiding_pairs(graph, 0, 2, {(1, 2)})
    assert dist == -1  # Can't reach 2 from 0 via 1
