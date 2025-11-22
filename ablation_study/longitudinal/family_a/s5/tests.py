import pytest
from solution import align


def verify_alignment(s1: str, s2: str, a1: str, a2: str) -> bool:
    """Verify alignment is valid."""
    # Same length
    if len(a1) != len(a2):
        return False
    # Remove gaps to get original
    if a1.replace('-', '') != s1:
        return False
    if a2.replace('-', '') != s2:
        return False
    # No double gaps
    for c1, c2 in zip(a1, a2):
        if c1 == '-' and c2 == '-':
            return False
    return True


def test_perfect_match():
    """Identical sequences."""
    score, a1, a2 = align("AGTC", "AGTC")
    assert score == 4
    assert a1 == "AGTC"
    assert a2 == "AGTC"


def test_one_mismatch():
    """Single mismatch."""
    score, a1, a2 = align("AGT", "ACT")
    # 2 matches (+2) + 1 mismatch (-1) = 1
    assert score == 1
    assert verify_alignment("AGT", "ACT", a1, a2)


def test_insertion():
    """Gap needed in first sequence."""
    score, a1, a2 = align("AC", "ABC")
    assert verify_alignment("AC", "ABC", a1, a2)
    # Expected: A-C / ABC or A_C / ABC
    assert '-' in a1 or '-' in a2


def test_deletion():
    """Gap needed in second sequence."""
    score, a1, a2 = align("ABC", "AC")
    assert verify_alignment("ABC", "AC", a1, a2)


def test_custom_scores():
    """Custom scoring parameters."""
    score, a1, a2 = align("AA", "AA", match=2, mismatch=-2, gap=-3)
    assert score == 4  # 2 matches * 2


def test_empty_strings():
    """Empty string alignment."""
    score, a1, a2 = align("", "ABC")
    assert verify_alignment("", "ABC", a1, a2)
    assert score == -3  # 3 gaps


def test_all_different():
    """No matching characters."""
    score, a1, a2 = align("AAA", "BBB")
    assert verify_alignment("AAA", "BBB", a1, a2)


def test_complex_alignment():
    """Complex case requiring multiple gaps."""
    score, a1, a2 = align("AGTACGCA", "TATGC")
    assert verify_alignment("AGTACGCA", "TATGC", a1, a2)
    assert len(a1) == len(a2)


def test_score_consistency():
    """Verify score matches alignment."""
    s1, s2 = "ACGT", "AGCT"
    score, a1, a2 = align(s1, s2, match=1, mismatch=-1, gap=-2)
    # Manually compute score from alignment
    computed = 0
    for c1, c2 in zip(a1, a2):
        if c1 == '-' or c2 == '-':
            computed -= 2
        elif c1 == c2:
            computed += 1
        else:
            computed -= 1
    assert score == computed
