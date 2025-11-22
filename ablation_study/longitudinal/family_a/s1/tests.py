import pytest
from solution import lcs


def test_basic():
    """Basic LCS."""
    result = lcs("ABCDEF", "AEBDF")
    assert len(result) == 4
    # Verify it's a valid subsequence of both
    assert is_subsequence(result, "ABCDEF")
    assert is_subsequence(result, "AEBDF")


def test_no_common():
    """No common characters."""
    assert lcs("ABC", "XYZ") == ""


def test_identical():
    """Identical strings."""
    assert lcs("HELLO", "HELLO") == "HELLO"


def test_one_empty():
    """Empty string."""
    assert lcs("", "ABC") == ""
    assert lcs("ABC", "") == ""


def test_single_char():
    """Single character strings."""
    assert lcs("A", "A") == "A"
    assert lcs("A", "B") == ""


def test_substring():
    """One is substring of other."""
    result = lcs("ABCD", "BC")
    assert result == "BC"


def test_interleaved():
    """Interleaved characters."""
    result = lcs("AXBYCZ", "ABC")
    assert result == "ABC"


# Helper function
def is_subsequence(sub: str, full: str) -> bool:
    """Check if sub is a subsequence of full."""
    it = iter(full)
    return all(c in it for c in sub)
