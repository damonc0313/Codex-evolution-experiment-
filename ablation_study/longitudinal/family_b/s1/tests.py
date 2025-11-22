import pytest
from solution import bfs_path


def is_valid_path(graph, path, start, end):
    """Verify path is valid."""
    if not path:
        return False
    if path[0] != start or path[-1] != end:
        return False
    for i in range(len(path) - 1):
        if path[i+1] not in graph.get(path[i], []):
            return False
    return True


def test_simple_path():
    graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
    path = bfs_path(graph, 0, 3)
    assert is_valid_path(graph, path, 0, 3)


def test_direct_edge():
    graph = {0: [1], 1: []}
    assert bfs_path(graph, 0, 1) == [0, 1]


def test_no_path():
    graph = {0: [1], 1: [], 2: [3], 3: []}
    assert bfs_path(graph, 0, 3) == []


def test_same_node():
    graph = {0: [1], 1: []}
    assert bfs_path(graph, 0, 0) == [0]


def test_longer_path():
    graph = {0: [1], 1: [2], 2: [3], 3: [4], 4: []}
    path = bfs_path(graph, 0, 4)
    assert path == [0, 1, 2, 3, 4]


def test_multiple_paths():
    graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
    path = bfs_path(graph, 0, 3)
    assert is_valid_path(graph, path, 0, 3)
    assert len(path) == 3  # BFS finds shortest


def test_cycle():
    graph = {0: [1], 1: [2], 2: [0, 3], 3: []}
    path = bfs_path(graph, 0, 3)
    assert is_valid_path(graph, path, 0, 3)
