import pytest
from solution import constrained_lcs


def test_basic_lcs():
    """Standard LCS with no forbidden chars."""
    assert constrained_lcs("ABCDEF", "ADBEF", set()) == "ABEF"


def test_forbidden_single_char():
    """Exclude character from LCS."""
    # "ADEF" is valid LCS of length 4 (A,D,E,F appear in order in both strings)
    assert constrained_lcs("ABCDEF", "ADBEF", {'B'}) == "ADEF"


def test_forbidden_multiple_chars():
    """Heavy constraints."""
    result = constrained_lcs("ABCDEF", "ADBEF", {'A', 'E', 'F'})
    # s1: B(1),C(2),D(3)  s2: D(1),B(2) - "BD" invalid (B after D in s2)
    # Only single chars valid: "B" or "D", lexicographically "B" < "D"
    assert result == "B" or result == "D"


def test_empty_strings():
    """Handle empty inputs."""
    assert constrained_lcs("", "ABC", set()) == ""
    assert constrained_lcs("ABC", "", set()) == ""
    assert constrained_lcs("", "", set()) == ""


def test_no_common_subsequence():
    """Completely different strings."""
    assert constrained_lcs("ABC", "XYZ", set()) == ""


def test_all_forbidden():
    """All chars forbidden."""
    assert constrained_lcs("ABC", "ABC", {'A', 'B', 'C'}) == ""


def test_identical_strings():
    """Same string."""
    assert constrained_lcs("ABCD", "ABCD", set()) == "ABCD"


def test_substring_relation():
    """One is substring of other."""
    assert constrained_lcs("ABCDEF", "BCD", set()) == "BCD"


def test_lexicographic_ordering():
    """Multiple LCS of same length - pick lexicographically smallest."""
    # s1: A(0),X(1),B(2),Y(3),C(4),Z(5)
    # s2: A(0),Z(1),B(2),Y(3),C(4),X(5)
    # LCS is "ABYC" (length 4) - appears in order in both
    result = constrained_lcs("AXBYCZ", "AZBYCX", set())
    assert len(result) == 4
    assert result == "ABYC"


def test_long_strings():
    """Performance on longer inputs."""
    s1 = "A" * 100 + "B" * 100
    s2 = "B" * 100 + "A" * 100
    result = constrained_lcs(s1, s2, set())
    assert len(result) == 100  # Either all A's or all B's


def test_complex_forbidden():
    """Complex constraint set."""
    s1 = "PROGRAMMING"
    s2 = "GAMING"
    result = constrained_lcs(s1, s2, {'A', 'M'})
    # LCS without A,M: should include G, I, N, G
    assert 'A' not in result
    assert 'M' not in result
