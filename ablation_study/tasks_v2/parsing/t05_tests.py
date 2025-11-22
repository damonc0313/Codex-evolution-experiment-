import pytest
from solution import parse_sexpr, eval_sexpr


def test_parse_atom():
    """Parse simple atoms."""
    assert parse_sexpr("42") == 42
    assert parse_sexpr("3.14") == 3.14
    assert parse_sexpr("hello") == "hello"


def test_parse_list():
    """Parse simple list."""
    result = parse_sexpr("(+ 1 2)")
    assert result == ["+", 1, 2]


def test_parse_nested():
    """Parse nested lists."""
    result = parse_sexpr("(+ (* 2 3) 4)")
    assert result == ["+", ["*", 2, 3], 4]


def test_eval_addition():
    """Evaluate addition."""
    expr = parse_sexpr("(+ 1 2 3)")
    assert eval_sexpr(expr) == 6


def test_eval_multiplication():
    """Evaluate multiplication."""
    expr = parse_sexpr("(* 2 3 4)")
    assert eval_sexpr(expr) == 24


def test_eval_subtraction():
    """Evaluate subtraction (binary)."""
    expr = parse_sexpr("(- 10 3)")
    assert eval_sexpr(expr) == 7


def test_eval_nested():
    """Evaluate nested expressions."""
    expr = parse_sexpr("(+ (* 2 3) (- 10 5))")
    assert eval_sexpr(expr) == 11


def test_eval_define():
    """Define and use variables."""
    env = {}
    define_expr = parse_sexpr("(define x 5)")
    eval_sexpr(define_expr, env)
    assert env["x"] == 5

    use_expr = parse_sexpr("(* x 2)")
    assert eval_sexpr(use_expr, env) == 10


def test_eval_multiple_vars():
    """Multiple variable definitions."""
    env = {}
    eval_sexpr(parse_sexpr("(define x 3)"), env)
    eval_sexpr(parse_sexpr("(define y 4)"), env)
    result = eval_sexpr(parse_sexpr("(+ x y)"), env)
    assert result == 7


def test_eval_undefined_symbol():
    """Raise error for undefined symbol."""
    expr = parse_sexpr("(+ x 5)")
    with pytest.raises((NameError, KeyError, ValueError)):
        eval_sexpr(expr, {})


def test_parse_whitespace():
    """Handle various whitespace."""
    result = parse_sexpr("(  +   1    2  )")
    assert result == ["+", 1, 2]


def test_parse_multiline():
    """Parse multi-line expression."""
    text = """(+
        (* 2 3)
        4)"""
    result = parse_sexpr(text)
    assert result == ["+", ["*", 2, 3], 4]


def test_eval_deep_nesting():
    """Deeply nested expressions."""
    expr = parse_sexpr("(+ (+ (+ 1 2) 3) 4)")
    assert eval_sexpr(expr) == 10


def test_parse_empty_list():
    """Parse empty list."""
    result = parse_sexpr("()")
    assert result == []


def test_eval_single_number():
    """Evaluate just a number."""
    assert eval_sexpr(42) == 42


def test_invalid_syntax():
    """Raise error for malformed expressions."""
    with pytest.raises((ValueError, SyntaxError)):
        parse_sexpr("(+ 1 2")  # Unmatched paren

    with pytest.raises((ValueError, SyntaxError)):
        parse_sexpr(")")  # Extra close paren


def test_eval_variable_in_nested():
    """Variables in nested contexts."""
    env = {"x": 5, "y": 3}
    expr = parse_sexpr("(+ (* x 2) y)")
    assert eval_sexpr(expr, env) == 13


def test_complex_expression():
    """Realistic complex S-expression."""
    env = {}
    eval_sexpr(parse_sexpr("(define radius 5)"), env)
    # Calculate area: pi * r^2 (simplified with pi=3)
    area_expr = parse_sexpr("(* 3 (* radius radius))")
    assert eval_sexpr(area_expr, env) == 75
