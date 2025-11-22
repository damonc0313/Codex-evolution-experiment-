import pytest
from solution import parse


def test_single_number():
    """Parse a single number."""
    tokens = [{"type": "NUMBER", "value": "42"}]
    result = parse(tokens)
    assert result == {"type": "NUMBER", "value": 42.0}


def test_single_identifier():
    """Parse a single identifier."""
    tokens = [{"type": "IDENTIFIER", "value": "x"}]
    result = parse(tokens)
    assert result == {"type": "IDENTIFIER", "name": "x"}


def test_simple_binop():
    """Parse simple binary operation."""
    tokens = [
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "4"}
    ]
    result = parse(tokens)
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {"type": "NUMBER", "value": 3.0},
        "right": {"type": "NUMBER", "value": 4.0}
    }


def test_left_associativity():
    """Operations are left-associative: 1 + 2 + 3 = (1 + 2) + 3."""
    tokens = [
        {"type": "NUMBER", "value": "1"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3"}
    ]
    result = parse(tokens)
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {
            "type": "BINOP",
            "op": "+",
            "left": {"type": "NUMBER", "value": 1.0},
            "right": {"type": "NUMBER", "value": 2.0}
        },
        "right": {"type": "NUMBER", "value": 3.0}
    }


def test_parentheses_grouping():
    """Parentheses override left-to-right: 1 + (2 + 3)."""
    tokens = [
        {"type": "NUMBER", "value": "1"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "LPAREN", "value": "("},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3"},
        {"type": "RPAREN", "value": ")"}
    ]
    result = parse(tokens)
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {"type": "NUMBER", "value": 1.0},
        "right": {
            "type": "BINOP",
            "op": "+",
            "left": {"type": "NUMBER", "value": 2.0},
            "right": {"type": "NUMBER", "value": 3.0}
        }
    }


def test_mixed_operators():
    """Mixed operators without precedence: 2 + 3 * 4 = (2 + 3) * 4."""
    tokens = [
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "4"}
    ]
    result = parse(tokens)
    # Without precedence, this is (2 + 3) * 4
    assert result == {
        "type": "BINOP",
        "op": "*",
        "left": {
            "type": "BINOP",
            "op": "+",
            "left": {"type": "NUMBER", "value": 2.0},
            "right": {"type": "NUMBER", "value": 3.0}
        },
        "right": {"type": "NUMBER", "value": 4.0}
    }


def test_identifier_in_expression():
    """Identifier in expression."""
    tokens = [
        {"type": "IDENTIFIER", "value": "x"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "2"}
    ]
    result = parse(tokens)
    assert result == {
        "type": "BINOP",
        "op": "*",
        "left": {"type": "IDENTIFIER", "name": "x"},
        "right": {"type": "NUMBER", "value": 2.0}
    }
