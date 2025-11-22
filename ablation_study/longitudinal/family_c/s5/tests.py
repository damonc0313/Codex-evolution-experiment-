import pytest
from solution import evaluate


def test_constant_expression():
    """Pure constant expression."""
    assert evaluate("3 + 4", {}) == 7.0


def test_simple_variable():
    """Single variable evaluation."""
    assert evaluate("x", {"x": 42}) == 42.0


def test_variable_addition():
    """Two variables addition."""
    assert evaluate("x + y", {"x": 3, "y": 4}) == 7.0


def test_variable_with_constants():
    """Mix of variables and constants."""
    assert evaluate("2 * x + 3", {"x": 5}) == 13.0


def test_precedence_with_variables():
    """Operator precedence with variables."""
    assert evaluate("x + y * z", {"x": 1, "y": 2, "z": 3}) == 7.0


def test_exponentiation():
    """Exponentiation with variables."""
    assert evaluate("x ^ 2 + y ^ 2", {"x": 3, "y": 4}) == 25.0


def test_complex_expression():
    """Complex nested expression."""
    assert evaluate("(a + b) * (c - d)", {"a": 2, "b": 3, "c": 10, "d": 4}) == 30.0


def test_undefined_variable():
    """Undefined variable raises NameError."""
    with pytest.raises(NameError):
        evaluate("x + 1", {})
