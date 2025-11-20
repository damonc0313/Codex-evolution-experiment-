import pytest
from solution import transform_pipeline

def test_single_transform():
    data = [1, 2, 3]
    result = transform_pipeline(data, lambda x: x * 2)
    assert result == [2, 4, 6]

def test_multiple_transforms():
    data = [1, 2, 3]
    result = transform_pipeline(
        data,
        lambda x: x * 2,
        lambda x: x + 1,
        lambda x: x ** 2
    )
    assert result == [9, 25, 49]  # ((1*2)+1)^2, ((2*2)+1)^2, ((3*2)+1)^2

def test_no_transforms():
    data = [1, 2, 3]
    result = transform_pipeline(data)
    assert result == [1, 2, 3]

def test_empty_data():
    result = transform_pipeline([], lambda x: x * 2)
    assert result == []

def test_string_transforms():
    data = ["hello", "world"]
    result = transform_pipeline(
        data,
        lambda s: s.upper(),
        lambda s: s + "!",
        lambda s: s[::-1]
    )
    assert result == ["!OLLEH", "!DLROW"]

def test_mixed_types():
    data = [5, 10, 15]
    result = transform_pipeline(
        data,
        lambda x: x / 2,
        lambda x: str(x),
        lambda x: x + " units"
    )
    assert result == ["2.5 units", "5.0 units", "7.5 units"]

def test_complex_transform():
    data = [{"value": 1}, {"value": 2}]
    result = transform_pipeline(
        data,
        lambda d: d["value"],
        lambda x: x * 10
    )
    assert result == [10, 20]
