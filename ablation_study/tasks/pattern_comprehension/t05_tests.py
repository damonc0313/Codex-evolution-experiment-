import pytest
from solution import group_stats

def test_basic_grouping():
    items = [
        {"team": "A", "score": 10},
        {"team": "B", "score": 20},
        {"team": "A", "score": 15}
    ]
    result = group_stats(items, "team", "score")
    assert result == {
        "A": {"count": 2, "sum": 25, "avg": 12.5},
        "B": {"count": 1, "sum": 20, "avg": 20.0}
    }

def test_single_group():
    items = [
        {"dept": "eng", "salary": 100000},
        {"dept": "eng", "salary": 120000}
    ]
    result = group_stats(items, "dept", "salary")
    assert result == {
        "eng": {"count": 2, "sum": 220000, "avg": 110000.0}
    }

def test_empty_input():
    result = group_stats([], "key", "value")
    assert result == {}

def test_single_item():
    items = [{"type": "x", "value": 42}]
    result = group_stats(items, "type", "value")
    assert result == {
        "x": {"count": 1, "sum": 42, "avg": 42.0}
    }

def test_many_groups():
    items = [
        {"color": "red", "price": 10},
        {"color": "blue", "price": 20},
        {"color": "green", "price": 15},
        {"color": "red", "price": 12}
    ]
    result = group_stats(items, "color", "price")
    assert result["red"] == {"count": 2, "sum": 22, "avg": 11.0}
    assert result["blue"] == {"count": 1, "sum": 20, "avg": 20.0}
    assert result["green"] == {"count": 1, "sum": 15, "avg": 15.0}

def test_missing_keys():
    items = [
        {"team": "A", "score": 10},
        {"team": "B"},  # Missing score
        {"score": 20},  # Missing team
        {"team": "A", "score": 15}
    ]
    result = group_stats(items, "team", "score")
    # Should only include items with both keys
    assert result == {
        "A": {"count": 2, "sum": 25, "avg": 12.5}
    }

def test_float_values():
    items = [
        {"cat": "x", "val": 1.5},
        {"cat": "x", "val": 2.5},
        {"cat": "y", "val": 3.0}
    ]
    result = group_stats(items, "cat", "val")
    assert result["x"]["sum"] == 4.0
    assert result["x"]["avg"] == 2.0
    assert result["y"]["avg"] == 3.0

def test_negative_values():
    items = [
        {"group": "A", "delta": -10},
        {"group": "A", "delta": 5},
        {"group": "A", "delta": -5}
    ]
    result = group_stats(items, "group", "delta")
    assert result["A"]["sum"] == -10
    assert result["A"]["avg"] == -10 / 3
