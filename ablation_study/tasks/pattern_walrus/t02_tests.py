import pytest
from solution import parse_config

def test_key_exists_valid():
    config = {"timeout": 30}
    assert parse_config(config, "timeout") == 30

def test_key_missing():
    config = {"other": 10}
    assert parse_config(config, "timeout", default=5) == 5

def test_value_below_minimum():
    config = {"retries": -1}
    assert parse_config(config, "retries", default=3, min_val=0) == 3

def test_value_at_minimum():
    config = {"retries": 0}
    assert parse_config(config, "retries", default=3, min_val=0) == 0

def test_non_integer_value():
    config = {"timeout": "invalid"}
    assert parse_config(config, "timeout", default=10) == 10

def test_float_value():
    config = {"timeout": 3.14}
    assert parse_config(config, "timeout", default=10) == 10

def test_none_value():
    config = {"timeout": None}
    assert parse_config(config, "timeout", default=5) == 5

def test_empty_config():
    assert parse_config({}, "key", default=42) == 42
