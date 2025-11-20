import pytest
from solution import safe_call

def test_successful_call():
    def add(a, b):
        return a + b

    result = safe_call(add, 2, 3)
    assert result == 5

def test_type_error():
    def strict_add(a: int, b: int) -> int:
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("Both arguments must be integers")
        return a + b

    result = safe_call(strict_add, "2", 3)
    assert result == "TYPE_ERROR"

def test_value_error():
    def positive_only(x):
        if x < 0:
            raise ValueError("Must be positive")
        return x

    result = safe_call(positive_only, -5)
    assert result == "VALUE_ERROR"

def test_other_error():
    def might_fail():
        raise RuntimeError("Unexpected error")

    result = safe_call(might_fail)
    assert result == "OTHER_ERROR"

def test_custom_error_values():
    def fail_type():
        raise TypeError()

    result = safe_call(fail_type, on_type_error="custom_type")
    assert result == "custom_type"

def test_all_custom_values():
    def fail_value():
        raise ValueError()

    result = safe_call(
        fail_value,
        on_type_error="t",
        on_value_error="v",
        on_other="o"
    )
    assert result == "v"

def test_key_error():
    def access_dict():
        d = {}
        return d["missing"]

    result = safe_call(access_dict, on_other="KEY_MISSING")
    assert result == "KEY_MISSING"

def test_zero_division():
    def divide():
        return 1 / 0

    result = safe_call(divide, on_other="DIV_ZERO")
    assert result == "DIV_ZERO"

def test_with_args():
    def power(base, exp):
        if exp < 0:
            raise ValueError("Negative exponent")
        return base ** exp

    assert safe_call(power, 2, 3) == 8
    assert safe_call(power, 2, -1) == "VALUE_ERROR"

def test_no_args():
    def get_value():
        return 42

    assert safe_call(get_value) == 42
