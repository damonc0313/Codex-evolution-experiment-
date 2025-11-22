import pytest
from solution import parse_and_eval


def test_basic_arithmetic():
    """Simple addition and multiplication."""
    assert parse_and_eval("2 + 3") == 5.0
    assert parse_and_eval("2 * 3") == 6.0
    assert parse_and_eval("10 - 4") == 6.0
    assert parse_and_eval("12 / 3") == 4.0


def test_operator_precedence():
    """Multiplication before addition."""
    assert parse_and_eval("2 + 3 * 4") == 14.0
    assert parse_and_eval("10 - 2 * 3") == 4.0
    assert parse_and_eval("6 / 2 + 1") == 4.0


def test_parentheses():
    """Parentheses override precedence."""
    assert parse_and_eval("(2 + 3) * 4") == 20.0
    assert parse_and_eval("10 / (2 + 3)") == 2.0
    assert parse_and_eval("((1 + 2) * (3 + 4))") == 21.0


def test_variables():
    """Use variables in expressions."""
    assert parse_and_eval("x + 5", {"x": 10}) == 15.0
    assert parse_and_eval("x * y", {"x": 3, "y": 4}) == 12.0
    assert parse_and_eval("a + b * c", {"a": 1, "b": 2, "c": 3}) == 7.0


def test_negative_numbers():
    """Handle negative values."""
    assert parse_and_eval("-5 + 10") == 5.0
    assert parse_and_eval("-3 * 4") == -12.0
    assert parse_and_eval("10 - -5") == 15.0


def test_whitespace():
    """Handle various whitespace."""
    assert parse_and_eval("2+3") == 5.0
    assert parse_and_eval("  2  +  3  ") == 5.0
    assert parse_and_eval("2\n+\t3") == 5.0


def test_undefined_variable():
    """Raise error for undefined variable."""
    with pytest.raises(ValueError):
        parse_and_eval("x + 5", {})
    with pytest.raises(ValueError):
        parse_and_eval("x + y", {"x": 5})


def test_invalid_syntax():
    """Raise error for malformed expressions."""
    with pytest.raises(ValueError):
        parse_and_eval("2 + + 3")
    with pytest.raises(ValueError):
        parse_and_eval("(2 + 3")  # Unmatched parenthesis


def test_division_by_zero():
    """Division by zero behavior."""
    result = parse_and_eval("1 / 0")
    assert result == float('inf') or result == float('-inf')


def test_complex_expression():
    """Nested operations with multiple variables."""
    expr = "(x + y) * (z - w) / 2"
    vars = {"x": 3, "y": 7, "z": 12, "w": 2}
    assert parse_and_eval(expr, vars) == 50.0


def test_single_number():
    """Expression is just a number."""
    assert parse_and_eval("42") == 42.0
    assert parse_and_eval("-17") == -17.0


def test_single_variable():
    """Expression is just a variable."""
    assert parse_and_eval("x", {"x": 99}) == 99.0


def test_float_numbers():
    """Support decimal numbers."""
    assert parse_and_eval("3.5 + 2.5") == 6.0
    assert parse_and_eval("10.5 / 2") == 5.25
