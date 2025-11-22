import pytest
from solution import dijkstra


def test_simple_shortest():
    graph = {0: [(1, 5), (2, 2)], 1: [(3, 1)], 2: [(1, 1), (3, 7)], 3: []}
    dist, path = dijkstra(graph, 0, 3)
    assert dist == 4  # 0->2->1->3: 2+1+1
    assert path[0] == 0 and path[-1] == 3


def test_direct_path():
    graph = {0: [(1, 10)], 1: []}
    dist, path = dijkstra(graph, 0, 1)
    assert dist == 10
    assert path == [0, 1]


def test_no_path():
    graph = {0: [(1, 5)], 1: [], 2: []}
    dist, path = dijkstra(graph, 0, 2)
    assert dist == -1
    assert path == []


def test_same_node():
    graph = {0: [(1, 5)], 1: []}
    dist, path = dijkstra(graph, 0, 0)
    assert dist == 0
    assert path == [0]


def test_longer_path_shorter_weight():
    # Longer path (more hops) but shorter total weight
    graph = {
        0: [(1, 10), (2, 1)],
        1: [(3, 1)],
        2: [(1, 1)],
        3: []
    }
    dist, path = dijkstra(graph, 0, 3)
    assert dist == 3  # 0->2->1->3: 1+1+1


def test_multiple_edges():
    graph = {0: [(1, 5), (1, 3)], 1: []}  # Multiple edges to same node
    dist, path = dijkstra(graph, 0, 1)
    assert dist == 3  # Takes shorter edge


def test_large_weights():
    graph = {0: [(1, 1000000)], 1: [(2, 1000000)], 2: []}
    dist, path = dijkstra(graph, 0, 2)
    assert dist == 2000000
