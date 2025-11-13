import pytest
from solution import safe_divide

def test_normal_division():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(7, 2) == 3.5

def test_division_by_zero():
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 0, default=0) == 0

def test_custom_default():
    assert safe_divide(5, 0, default=-1) == -1
    assert safe_divide(5, 0, default=float('inf')) == float('inf')

def test_negative_numbers():
    assert safe_divide(-10, 2) == -5.0
    assert safe_divide(10, -2) == -5.0

def test_float_division():
    assert safe_divide(1, 3) == pytest.approx(0.333333, rel=1e-5)

def test_zero_numerator():
    assert safe_divide(0, 5) == 0.0

def test_large_numbers():
    assert safe_divide(1e10, 1e5) == 1e5

def test_very_small_divisor():
    result = safe_divide(1, 1e-10)
    assert result > 1e9
