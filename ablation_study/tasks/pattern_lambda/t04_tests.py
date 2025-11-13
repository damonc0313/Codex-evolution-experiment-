import pytest
from solution import custom_reduce

def test_sum():
    assert custom_reduce([1, 2, 3, 4], "sum") == 10

def test_sum_with_initial():
    assert custom_reduce([1, 2, 3], "sum", initial=10) == 16

def test_product():
    assert custom_reduce([2, 3, 4], "product") == 24

def test_product_with_initial():
    assert custom_reduce([2, 3], "product", initial=5) == 30

def test_concat():
    assert custom_reduce(["hello", " ", "world"], "concat") == "hello world"

def test_concat_with_initial():
    assert custom_reduce([" ", "world"], "concat", initial="hello") == "hello world"

def test_min():
    assert custom_reduce([5, 2, 8, 1, 9], "min") == 1

def test_max():
    assert custom_reduce([5, 2, 8, 1, 9], "max") == 9

def test_and():
    assert custom_reduce([True, True, True], "and") is True
    assert custom_reduce([True, False, True], "and") is False

def test_or():
    assert custom_reduce([False, False, True], "or") is True
    assert custom_reduce([False, False, False], "or") is False

def test_empty_list_sum():
    assert custom_reduce([], "sum") == 0

def test_empty_list_product():
    assert custom_reduce([], "product") == 1

def test_empty_list_concat():
    assert custom_reduce([], "concat") == ""

def test_invalid_operation():
    with pytest.raises(ValueError):
        custom_reduce([1, 2, 3], "invalid")

def test_single_element():
    assert custom_reduce([42], "sum") == 42
    assert custom_reduce([7], "product") == 7
