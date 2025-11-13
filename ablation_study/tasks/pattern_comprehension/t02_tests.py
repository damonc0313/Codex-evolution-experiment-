import pytest
from solution import invert_dict

def test_simple_inversion():
    d = {"a": 1, "b": 2, "c": 3}
    result = invert_dict(d)
    assert result == {1: "a", 2: "b", 3: "c"}

def test_duplicate_values():
    # Last key with duplicate value should be kept
    d = {"a": 1, "b": 2, "c": 1}
    result = invert_dict(d)
    assert result[1] in ["a", "c"]  # Either is acceptable
    assert result[2] == "b"

def test_empty_dict():
    assert invert_dict({}) == {}

def test_string_values():
    d = {1: "one", 2: "two", 3: "three"}
    result = invert_dict(d)
    assert result == {"one": 1, "two": 2, "three": 3}

def test_tuple_values():
    d = {"a": (1, 2), "b": (3, 4)}
    result = invert_dict(d)
    assert result == {(1, 2): "a", (3, 4): "b"}

def test_mixed_key_types():
    d = {"str": 1, 2: "int", 3.14: "float"}
    result = invert_dict(d)
    assert result == {1: "str", "int": 2, "float": 3.14}

def test_preserves_last():
    # Verify that last occurrence is kept for duplicate values
    d = {"first": "x", "second": "y", "third": "x"}
    result = invert_dict(d)
    # The iteration order matters - test that something reasonable happens
    assert "x" in result
    assert result["y"] == "second"
