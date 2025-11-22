import pytest
from solution import matrix_chain_order


def test_three_matrices():
    """Classic 3-matrix example."""
    dims = [10, 20, 30, 40]
    ops, paren = matrix_chain_order(dims)
    assert ops == 18000  # Optimal: ((A0A1)A2)
    assert "A0" in paren and "A1" in paren and "A2" in paren


def test_single_matrix():
    """One matrix - no multiplications."""
    dims = [10, 20]
    ops, paren = matrix_chain_order(dims)
    assert ops == 0
    assert paren == "A0"


def test_two_matrices():
    """Two matrices - only one way."""
    dims = [10, 20, 30]
    ops, paren = matrix_chain_order(dims)
    assert ops == 10 * 20 * 30
    assert paren == "(A0A1)"


def test_empty_input():
    """No matrices."""
    ops, paren = matrix_chain_order([])
    assert ops == 0
    assert paren == ""


def test_four_matrices():
    """More complex case."""
    dims = [5, 10, 3, 12, 5]
    ops, paren = matrix_chain_order(dims)
    # Verify it computes something reasonable
    assert ops > 0
    assert paren.count("A") == 4  # Four matrices


def test_parenthesization_format():
    """Check parenthesization is well-formed."""
    dims = [10, 20, 30, 40]
    _, paren = matrix_chain_order(dims)
    # Should have matching parens
    assert paren.count('(') == paren.count(')')
    # Should reference all matrices
    assert "A0" in paren and "A1" in paren and "A2" in paren
