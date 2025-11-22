import pytest
from solution import large_sccs


def test_single_large_scc():
    """One large SCC."""
    graph = {0: [1], 1: [2], 2: [0]}
    result = large_sccs(graph, 2)
    assert len(result) == 1
    assert set(result[0]) == {0, 1, 2}


def test_filter_small_sccs():
    """Filter out SCCs below threshold."""
    graph = {
        0: [1], 1: [2], 2: [0],  # SCC of 3
        3: [4], 4: [3],           # SCC of 2
        5: []                      # SCC of 1
    }
    result = large_sccs(graph, 2)
    assert len(result) == 2  # First two SCCs


def test_size_ordering():
    """Larger SCCs first."""
    graph = {
        0: [1], 1: [2], 2: [0],  # Size 3
        3: [4], 4: [3]            # Size 2
    }
    result = large_sccs(graph, 2)
    assert len(result[0]) > len(result[1])


def test_tie_breaking():
    """Same size - order by smallest node."""
    graph = {
        0: [1], 1: [0],  # SCC: {0,1}
        2: [3], 3: [2]   # SCC: {2,3}
    }
    result = large_sccs(graph, 2)
    # Both size 2, order by min node: {0,1} before {2,3}
    assert result[0][0] < result[1][0]


def test_dag_no_sccs():
    """DAG has no non-trivial SCCs."""
    graph = {0: [1], 1: [2], 2: []}
    result = large_sccs(graph, 2)
    assert result == []


def test_empty_graph():
    """No nodes."""
    result = large_sccs({}, 1)
    assert result == []


def test_all_trivial_sccs():
    """All SCCs size 1."""
    graph = {0: [1], 1: [2], 2: []}
    result = large_sccs(graph, 2)
    assert result == []


def test_nodes_sorted_in_scc():
    """Each SCC's nodes are sorted."""
    graph = {3: [2], 2: [1], 1: [3]}
    result = large_sccs(graph, 2)
    assert result[0] == sorted(result[0])
