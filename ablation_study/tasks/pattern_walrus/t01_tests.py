import pytest
from solution import process_valid_lines

def test_basic_filtering():
    lines = ["hello world", "hi", "testing", "a"]
    result = process_valid_lines(lines)
    assert result == ["HELLO WORLD", "TESTING"]

def test_empty_input():
    assert process_valid_lines([]) == []

def test_no_valid_lines():
    lines = ["a", "hi", "bye", "ok"]
    assert process_valid_lines(lines) == []

def test_all_valid_lines():
    lines = ["longer", "strings", "example"]
    result = process_valid_lines(lines)
    assert result == ["LONGER", "STRINGS", "EXAMPLE"]

def test_edge_length():
    lines = ["exact", "exactly", "short"]
    result = process_valid_lines(lines)
    assert result == ["EXACTLY"]

def test_very_long_string():
    long_str = "a" * 1000
    result = process_valid_lines([long_str])
    assert result == [long_str.upper()]

def test_mixed_whitespace():
    lines = ["  spaces  ", "tabs\t\t", "x"]
    result = process_valid_lines(lines)
    assert result == ["  SPACES  ", "TABS\t\t"]
