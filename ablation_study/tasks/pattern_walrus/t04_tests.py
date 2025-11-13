import pytest
from solution import match_and_extract

def test_single_group():
    text = "User: alice"
    pattern = r"User: (?P<name>\w+)"
    result = match_and_extract(text, pattern)
    assert result == {"name": "alice"}

def test_multiple_groups():
    text = "2025-11-13"
    pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    result = match_and_extract(text, pattern)
    assert result == {"year": "2025", "month": "11", "day": "13"}

def test_no_match():
    text = "No pattern here"
    pattern = r"(?P<number>\d+)"
    result = match_and_extract(text, pattern)
    assert result is None

def test_empty_text():
    result = match_and_extract("", r"(?P<any>.+)")
    assert result is None

def test_email_extraction():
    text = "Contact: bob@example.com"
    pattern = r"(?P<user>\w+)@(?P<domain>[\w.]+)"
    result = match_and_extract(text, pattern)
    assert result == {"user": "bob", "domain": "example.com"}

def test_partial_match():
    text = "Price: $99.99 and more"
    pattern = r"\$(?P<amount>[\d.]+)"
    result = match_and_extract(text, pattern)
    assert result == {"amount": "99.99"}

def test_complex_pattern():
    text = "HTTP/1.1 404 Not Found"
    pattern = r"HTTP/(?P<version>[\d.]+)\s+(?P<code>\d+)\s+(?P<msg>.+)"
    result = match_and_extract(text, pattern)
    assert result == {"version": "1.1", "code": "404", "msg": "Not Found"}
