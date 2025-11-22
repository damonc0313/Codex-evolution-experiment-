import pytest
from solution import parse_with_precedence


def test_simple_addition():
    """Parse simple addition."""
    tokens = [
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "4"}
    ]
    result = parse_with_precedence(tokens)
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {"type": "NUMBER", "value": 3.0},
        "right": {"type": "NUMBER", "value": 4.0}
    }


def test_multiplication_precedence():
    """Multiplication before addition: 2 + 3 * 4 = 2 + (3 * 4)."""
    tokens = [
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "4"}
    ]
    result = parse_with_precedence(tokens)
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {"type": "NUMBER", "value": 2.0},
        "right": {
            "type": "BINOP",
            "op": "*",
            "left": {"type": "NUMBER", "value": 3.0},
            "right": {"type": "NUMBER", "value": 4.0}
        }
    }


def test_division_precedence():
    """Division before subtraction: 10 - 6 / 2 = 10 - (6 / 2)."""
    tokens = [
        {"type": "NUMBER", "value": "10"},
        {"type": "OPERATOR", "value": "-"},
        {"type": "NUMBER", "value": "6"},
        {"type": "OPERATOR", "value": "/"},
        {"type": "NUMBER", "value": "2"}
    ]
    result = parse_with_precedence(tokens)
    assert result == {
        "type": "BINOP",
        "op": "-",
        "left": {"type": "NUMBER", "value": 10.0},
        "right": {
            "type": "BINOP",
            "op": "/",
            "left": {"type": "NUMBER", "value": 6.0},
            "right": {"type": "NUMBER", "value": 2.0}
        }
    }


def test_exponent_precedence():
    """Exponent has highest precedence: 2 * 3 ^ 2 = 2 * (3 ^ 2)."""
    tokens = [
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "^"},
        {"type": "NUMBER", "value": "2"}
    ]
    result = parse_with_precedence(tokens)
    assert result == {
        "type": "BINOP",
        "op": "*",
        "left": {"type": "NUMBER", "value": 2.0},
        "right": {
            "type": "BINOP",
            "op": "^",
            "left": {"type": "NUMBER", "value": 3.0},
            "right": {"type": "NUMBER", "value": 2.0}
        }
    }


def test_exponent_right_associative():
    """Exponent is right-associative: 2 ^ 3 ^ 2 = 2 ^ (3 ^ 2)."""
    tokens = [
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "^"},
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "^"},
        {"type": "NUMBER", "value": "2"}
    ]
    result = parse_with_precedence(tokens)
    # Right associative: 2^(3^2)
    assert result == {
        "type": "BINOP",
        "op": "^",
        "left": {"type": "NUMBER", "value": 2.0},
        "right": {
            "type": "BINOP",
            "op": "^",
            "left": {"type": "NUMBER", "value": 3.0},
            "right": {"type": "NUMBER", "value": 2.0}
        }
    }


def test_parentheses_override():
    """Parentheses override precedence: (2 + 3) * 4."""
    tokens = [
        {"type": "LPAREN", "value": "("},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3"},
        {"type": "RPAREN", "value": ")"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "4"}
    ]
    result = parse_with_precedence(tokens)
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


def test_complex_precedence():
    """Complex expression: 1 + 2 * 3 ^ 2 - 4 / 2."""
    tokens = [
        {"type": "NUMBER", "value": "1"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "^"},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "-"},
        {"type": "NUMBER", "value": "4"},
        {"type": "OPERATOR", "value": "/"},
        {"type": "NUMBER", "value": "2"}
    ]
    result = parse_with_precedence(tokens)
    # 1 + (2 * (3 ^ 2)) - (4 / 2)
    # = (1 + (2 * (3^2))) - (4/2)
    expected = {
        "type": "BINOP",
        "op": "-",
        "left": {
            "type": "BINOP",
            "op": "+",
            "left": {"type": "NUMBER", "value": 1.0},
            "right": {
                "type": "BINOP",
                "op": "*",
                "left": {"type": "NUMBER", "value": 2.0},
                "right": {
                    "type": "BINOP",
                    "op": "^",
                    "left": {"type": "NUMBER", "value": 3.0},
                    "right": {"type": "NUMBER", "value": 2.0}
                }
            }
        },
        "right": {
            "type": "BINOP",
            "op": "/",
            "left": {"type": "NUMBER", "value": 4.0},
            "right": {"type": "NUMBER", "value": 2.0}
        }
    }
    assert result == expected
