import pytest
from solution import floyd_warshall


def test_simple_graph():
    graph = {0: [(1, 5)], 1: [(2, 3)], 2: []}
    result = floyd_warshall(graph)
    assert result[(0, 1)] == 5
    assert result[(0, 2)] == 8
    assert result[(1, 2)] == 3


def test_self_distance():
    graph = {0: [(1, 5)], 1: []}
    result = floyd_warshall(graph)
    assert result[(0, 0)] == 0
    assert result[(1, 1)] == 0


def test_unreachable():
    graph = {0: [], 1: []}
    result = floyd_warshall(graph)
    assert result[(0, 1)] == float('inf')


def test_triangle():
    graph = {
        0: [(1, 1), (2, 4)],
        1: [(2, 2)],
        2: []
    }
    result = floyd_warshall(graph)
    assert result[(0, 2)] == 3  # 0->1->2 shorter than 0->2


def test_bidirectional():
    graph = {
        0: [(1, 5)],
        1: [(0, 3), (2, 2)],
        2: []
    }
    result = floyd_warshall(graph)
    assert result[(0, 1)] == 5
    assert result[(1, 0)] == 3


def test_larger_graph():
    graph = {
        0: [(1, 1), (2, 5)],
        1: [(2, 2), (3, 6)],
        2: [(3, 1)],
        3: []
    }
    result = floyd_warshall(graph)
    assert result[(0, 3)] == 4  # 0->1->2->3
