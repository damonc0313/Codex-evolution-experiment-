import pytest
from solution import multi_lcs


def is_subsequence(sub: str, full: str) -> bool:
    it = iter(full)
    return all(c in it for c in sub)


def test_single_string():
    """LCS of single string is itself."""
    assert multi_lcs(["ABC"]) == "ABC"


def test_two_strings():
    """Two strings - like regular LCS."""
    result = multi_lcs(["ABCD", "ABDC"])
    assert len(result) >= 3
    assert is_subsequence(result, "ABCD")
    assert is_subsequence(result, "ABDC")


def test_three_strings():
    """Three strings reduce options."""
    result = multi_lcs(["ABC", "BAC", "CAB"])
    # Each pair shares only 2 chars in common order
    assert len(result) >= 1
    for s in ["ABC", "BAC", "CAB"]:
        assert is_subsequence(result, s)


def test_no_common():
    """No common characters."""
    assert multi_lcs(["XYZ", "ABC"]) == ""


def test_identical():
    """All identical strings."""
    assert multi_lcs(["HELLO", "HELLO", "HELLO"]) == "HELLO"


def test_prefix_suffix():
    """Common prefix/suffix."""
    result = multi_lcs(["ABC", "ABXC", "ABYC"])
    assert is_subsequence(result, "ABC")
    # Common: A, B, C in order
    assert len(result) >= 3


def test_empty_in_list():
    """Empty string means empty result."""
    assert multi_lcs(["ABC", "", "DEF"]) == ""


def test_many_strings():
    """5 strings."""
    strings = ["ABCDEF", "ABXDEF", "ABYDEF", "ABZDEF", "ABWDEF"]
    result = multi_lcs(strings)
    # All share "ABDEF"
    assert len(result) >= 5
