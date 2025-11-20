import pytest
from solution import compose

def test_single_function():
    f = lambda x: x * 2
    composed = compose(f)
    assert composed(5) == 10

def test_two_functions():
    f = lambda x: x * 2
    g = lambda x: x + 3
    composed = compose(f, g)  # f(g(x))
    assert composed(5) == 16  # (5 + 3) * 2

def test_three_functions():
    f = lambda x: x * 2
    g = lambda x: x + 3
    h = lambda x: x ** 2
    composed = compose(f, g, h)  # f(g(h(x)))
    assert composed(4) == 38  # ((4^2) + 3) * 2 = (16 + 3) * 2 = 38

def test_string_functions():
    upper = lambda s: s.upper()
    reverse = lambda s: s[::-1]
    exclaim = lambda s: s + "!"
    composed = compose(exclaim, upper, reverse)
    assert composed("hello") == "OLLEH!"

def test_no_functions():
    composed = compose()
    assert composed(42) == 42
    assert composed("test") == "test"

def test_many_functions():
    fns = [lambda x: x + 1] * 5
    composed = compose(*fns)
    assert composed(0) == 5

def test_mixed_types():
    str_fn = lambda x: str(x)
    len_fn = lambda x: len(x)
    double_fn = lambda x: x * 2
    composed = compose(double_fn, len_fn, str_fn)
    assert composed(12345) == 10  # len("12345") * 2 = 5 * 2 = 10

def test_composition_order():
    # Verify right-to-left application
    div2 = lambda x: x / 2
    sub1 = lambda x: x - 1
    composed = compose(div2, sub1)
    assert composed(10) == 4.5  # (10 - 1) / 2 = 4.5

    # Reverse order should give different result
    composed_rev = compose(sub1, div2)
    assert composed_rev(10) == 4.0  # (10 / 2) - 1 = 4.0
