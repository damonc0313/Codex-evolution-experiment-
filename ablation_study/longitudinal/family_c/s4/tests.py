import pytest
from solution import build_ast


def test_constant_fold_addition():
    """Constant expression fully folded."""
    result = build_ast("3 + 4")
    assert result == {"type": "NUMBER", "value": 7.0}


def test_constant_fold_complex():
    """Multi-operator constant expression folded."""
    result = build_ast("2 * 3 + 4")
    # 2*3=6, 6+4=10
    assert result == {"type": "NUMBER", "value": 10.0}


def test_constant_fold_precedence():
    """Precedence respected in constant folding."""
    result = build_ast("2 + 3 * 4")
    # 3*4=12, 2+12=14
    assert result == {"type": "NUMBER", "value": 14.0}


def test_constant_fold_exponent():
    """Exponentiation constant folding."""
    result = build_ast("2 ^ 3")
    assert result == {"type": "NUMBER", "value": 8.0}


def test_partial_fold_with_identifier():
    """Partial folding when identifier present."""
    result = build_ast("x + (3 + 4)")
    # (3 + 4) folds to 7, but x + 7 cannot fold
    assert result == {
        "type": "BINOP",
        "op": "+",
        "left": {"type": "IDENTIFIER", "name": "x"},
        "right": {"type": "NUMBER", "value": 7.0}
    }


def test_no_fold_identifier_expression():
    """Cannot fold when identifiers involved."""
    result = build_ast("x * 2")
    assert result == {
        "type": "BINOP",
        "op": "*",
        "left": {"type": "IDENTIFIER", "name": "x"},
        "right": {"type": "NUMBER", "value": 2.0}
    }


def test_nested_constant_fold():
    """Nested constant expressions all fold."""
    result = build_ast("(1 + 2) * (3 + 4)")
    # (1+2)=3, (3+4)=7, 3*7=21
    assert result == {"type": "NUMBER", "value": 21.0}
