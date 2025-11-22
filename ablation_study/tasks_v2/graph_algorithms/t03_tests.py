import pytest
from solution import constrained_mst


def test_simple_mst():
    """Basic MST with no constraints."""
    edges = [(0,1,1), (0,2,4), (1,2,2), (1,3,5), (2,3,3)]
    weight, mst = constrained_mst(edges, 4, set())
    assert weight == 6  # Edges (0,1), (1,2), (2,3)
    assert len(mst) == 3


def test_required_edges_included():
    """MST must include required edges."""
    edges = [(0,1,1), (0,2,4), (1,2,2), (1,3,5), (2,3,3)]
    weight, mst = constrained_mst(edges, 4, {(0,1), (2,3)})
    # Must include (0,1) and (2,3)
    assert (0,1) in mst or (1,0) in mst
    assert (2,3) in mst or (3,2) in mst
    assert weight == 6


def test_required_forms_cycle():
    """Required edges form a cycle - impossible."""
    edges = [(0,1,1), (1,2,2), (2,0,3), (0,3,4)]
    weight, mst = constrained_mst(edges, 4, {(0,1), (1,2), (2,0)})
    assert weight == -1
    assert mst == []


def test_disconnected_graph():
    """Graph not connected."""
    edges = [(0,1,1), (2,3,2)]
    weight, mst = constrained_mst(edges, 4, set())
    assert weight == -1


def test_single_edge():
    """Single edge graph."""
    edges = [(0,1,5)]
    weight, mst = constrained_mst(edges, 2, set())
    assert weight == 5
    assert len(mst) == 1


def test_required_makes_suboptimal():
    """Required edges force suboptimal MST."""
    edges = [(0,1,1), (1,2,1), (0,2,10)]
    weight, mst = constrained_mst(edges, 3, {(0,2)})
    # Without constraint: weight = 2
    # With (0,2) required: weight = 11
    assert weight == 11


def test_bidirectional_edges():
    """Edge (u,v) same as (v,u)."""
    edges = [(0,1,5), (1,0,5)]  # Same edge listed twice
    weight, mst = constrained_mst(edges, 2, {(1,0)})
    assert weight == 5
