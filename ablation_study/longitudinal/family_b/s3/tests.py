import pytest
from solution import constrained_shortest


def test_no_constraint():
    graph = {0: [(1, 5), (2, 2)], 1: [(3, 1)], 2: [(3, 7)], 3: []}
    dist, path = constrained_shortest(graph, 0, 3, set())
    assert dist == 6  # 0->1->3


def test_single_required():
    graph = {0: [(1, 5), (2, 2)], 1: [(3, 1)], 2: [(1, 1), (3, 7)], 3: []}
    dist, path = constrained_shortest(graph, 0, 3, {2})
    assert 2 in path
    assert path[0] == 0 and path[-1] == 3


def test_impossible():
    graph = {0: [(1, 5)], 1: [(2, 5)], 2: [], 3: []}
    dist, path = constrained_shortest(graph, 0, 2, {3})
    assert dist == -1  # Can't reach node 3


def test_multiple_required():
    graph = {
        0: [(1, 1), (2, 1)],
        1: [(3, 1)],
        2: [(3, 1)],
        3: [(4, 1)],
        4: []
    }
    dist, path = constrained_shortest(graph, 0, 4, {1, 2})
    # Must visit both 1 and 2
    assert 1 in path and 2 in path


def test_required_is_start():
    graph = {0: [(1, 5)], 1: []}
    dist, path = constrained_shortest(graph, 0, 1, {0})
    assert dist == 5
    assert path == [0, 1]


def test_required_is_end():
    graph = {0: [(1, 5)], 1: []}
    dist, path = constrained_shortest(graph, 0, 1, {1})
    assert dist == 5
    assert path == [0, 1]
