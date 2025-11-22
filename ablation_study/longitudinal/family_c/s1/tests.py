import pytest
from solution import tokenize


def test_simple_addition():
    """Basic addition expression."""
    result = tokenize("3 + 4")
    assert result == [
        {"type": "NUMBER", "value": "3"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "4"}
    ]


def test_all_operators():
    """All arithmetic operators."""
    result = tokenize("1 + 2 - 3 * 4 / 5 ^ 6")
    assert len(result) == 11
    operators = [t["value"] for t in result if t["type"] == "OPERATOR"]
    assert operators == ["+", "-", "*", "/", "^"]


def test_parentheses():
    """Parentheses grouping."""
    result = tokenize("(1 + 2)")
    assert result == [
        {"type": "LPAREN", "value": "("},
        {"type": "NUMBER", "value": "1"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "2"},
        {"type": "RPAREN", "value": ")"}
    ]


def test_identifiers():
    """Variable identifiers."""
    result = tokenize("x + y * z")
    assert result == [
        {"type": "IDENTIFIER", "value": "x"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "IDENTIFIER", "value": "y"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "IDENTIFIER", "value": "z"}
    ]


def test_floating_point():
    """Decimal numbers."""
    result = tokenize("3.14 + 2.71")
    assert result == [
        {"type": "NUMBER", "value": "3.14"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "2.71"}
    ]


def test_no_whitespace():
    """Expression without spaces."""
    result = tokenize("1+2*3")
    assert result == [
        {"type": "NUMBER", "value": "1"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "2"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "NUMBER", "value": "3"}
    ]


def test_complex_expression():
    """Complex nested expression."""
    result = tokenize("(foo + 3.5) * (bar - 2)")
    assert result == [
        {"type": "LPAREN", "value": "("},
        {"type": "IDENTIFIER", "value": "foo"},
        {"type": "OPERATOR", "value": "+"},
        {"type": "NUMBER", "value": "3.5"},
        {"type": "RPAREN", "value": ")"},
        {"type": "OPERATOR", "value": "*"},
        {"type": "LPAREN", "value": "("},
        {"type": "IDENTIFIER", "value": "bar"},
        {"type": "OPERATOR", "value": "-"},
        {"type": "NUMBER", "value": "2"},
        {"type": "RPAREN", "value": ")"}
    ]
