import pytest
from solution import parse_json

def test_valid_dict():
    result = parse_json('{"name": "Alice", "age": 30}')
    assert result == {"name": "Alice", "age": 30}

def test_valid_list():
    result = parse_json('[1, 2, 3, 4]')
    assert result == [1, 2, 3, 4]

def test_valid_string():
    result = parse_json('"hello"')
    assert result == "hello"

def test_valid_number():
    result = parse_json('42')
    assert result == 42

def test_valid_boolean():
    assert parse_json('true') is True
    assert parse_json('false') is False

def test_valid_null():
    assert parse_json('null') is None

def test_invalid_json():
    result = parse_json('{invalid json}', default={})
    assert result == {}

def test_empty_string():
    result = parse_json('', default=[])
    assert result == []

def test_none_input():
    result = parse_json(None, default={"error": True})
    assert result == {"error": True}

def test_default_none():
    result = parse_json('invalid')
    assert result is None

def test_malformed_json():
    result = parse_json('{"key": undefined}', default={"fallback": True})
    assert result == {"fallback": True}

def test_truncated_json():
    result = parse_json('{"key":', default=[])
    assert result == []

def test_nested_valid():
    result = parse_json('{"outer": {"inner": [1, 2, 3]}}')
    assert result == {"outer": {"inner": [1, 2, 3]}}
