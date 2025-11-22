import pytest
from solution import constrained_lcs


def test_basic_constraint():
    """LCS with required characters."""
    result = constrained_lcs("ABCDEF", "AEBDF", "AD")
    assert 'A' in result and 'D' in result
    assert len(result) >= 2


def test_impossible():
    """Required chars not available."""
    assert constrained_lcs("ABCDEF", "AEBDF", "XY") == ""


def test_no_constraint():
    """Empty constraint = regular LCS."""
    result = constrained_lcs("ABC", "ABC", "")
    assert result == "ABC"


def test_full_constraint():
    """All LCS chars required."""
    result = constrained_lcs("ABC", "ABC", "ABC")
    assert result == "ABC"


def test_single_required():
    """Single required char."""
    result = constrained_lcs("AXBXC", "ABC", "B")
    assert 'B' in result
    assert len(result) >= 1


def test_constraint_forces_shorter():
    """Constraint may force shorter LCS."""
    # Without constraint: LCS could be "AC" (length 2)
    # With constraint "B": LCS must be "B" (length 1) if B not in both
    result = constrained_lcs("AXC", "AYC", "B")
    assert result == ""  # B not in common


def test_multiple_paths():
    """Multiple valid LCS paths."""
    result = constrained_lcs("ABAB", "ABAB", "A")
    assert 'A' in result
    assert len(result) >= 2
