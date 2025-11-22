import pytest
from solution import tsp_nearest_neighbor


def test_triangle():
    distances = {
        (0, 1): 1, (1, 0): 1,
        (0, 2): 2, (2, 0): 2,
        (1, 2): 3, (2, 1): 3
    }
    dist, tour = tsp_nearest_neighbor(distances, 0)
    # Starting from 0, nearest is 1, then 2, back to 0
    assert tour[0] == 0
    assert tour[-1] == 0
    assert set(tour[:-1]) == {0, 1, 2}


def test_square():
    distances = {
        (0, 1): 1, (1, 0): 1,
        (0, 2): 10, (2, 0): 10,
        (0, 3): 1, (3, 0): 1,
        (1, 2): 1, (2, 1): 1,
        (1, 3): 10, (3, 1): 10,
        (2, 3): 1, (3, 2): 1
    }
    dist, tour = tsp_nearest_neighbor(distances, 0)
    # Should visit all nodes and return
    assert len(tour) == 5  # 4 nodes + return to start
    assert tour[0] == tour[-1] == 0
    assert set(tour[:-1]) == {0, 1, 2, 3}


def test_two_nodes():
    distances = {(0, 1): 5, (1, 0): 5}
    dist, tour = tsp_nearest_neighbor(distances, 0)
    assert dist == 10  # Out and back
    assert tour == [0, 1, 0]


def test_single_node():
    distances = {}
    dist, tour = tsp_nearest_neighbor(distances, 0)
    assert dist == 0
    assert tour == [0]


def test_greedy_choice():
    # Nearest neighbor may not find optimal
    distances = {
        (0, 1): 1, (1, 0): 1,
        (0, 2): 2, (2, 0): 2,
        (1, 2): 10, (2, 1): 10
    }
    dist, tour = tsp_nearest_neighbor(distances, 0)
    # Greedy: 0->1->2->0 = 1+10+2 = 13
    # Optimal: 0->2->1->0 = 2+10+1 = 13 (same in this case)
    assert tour[0] == 0
    assert tour[-1] == 0
