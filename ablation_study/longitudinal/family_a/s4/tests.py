import pytest
from solution import diff


def apply_diff(s1: str, ops: list[tuple[str, str]]) -> str:
    """Apply diff operations to verify correctness."""
    result = []
    s1_idx = 0
    for op, char in ops:
        if op == "keep":
            assert s1[s1_idx] == char, f"Keep mismatch at {s1_idx}"
            result.append(char)
            s1_idx += 1
        elif op == "del":
            assert s1[s1_idx] == char, f"Del mismatch at {s1_idx}"
            s1_idx += 1
        elif op == "add":
            result.append(char)
    return "".join(result)


def test_simple_replace():
    """Replace last char."""
    ops = diff("ABC", "ABD")
    result = apply_diff("ABC", ops)
    assert result == "ABD"


def test_identical():
    """Identical strings - all keeps."""
    ops = diff("ABC", "ABC")
    assert all(op[0] == "keep" for op in ops)
    assert apply_diff("ABC", ops) == "ABC"


def test_empty_to_string():
    """Add all characters."""
    ops = diff("", "ABC")
    assert all(op[0] == "add" for op in ops)
    assert apply_diff("", ops) == "ABC"


def test_string_to_empty():
    """Delete all characters."""
    ops = diff("ABC", "")
    assert all(op[0] == "del" for op in ops)
    assert apply_diff("ABC", ops) == ""


def test_insert_middle():
    """Insert in middle."""
    ops = diff("AC", "ABC")
    result = apply_diff("AC", ops)
    assert result == "ABC"


def test_delete_middle():
    """Delete from middle."""
    ops = diff("ABC", "AC")
    result = apply_diff("ABC", ops)
    assert result == "AC"


def test_complex():
    """Multiple edits."""
    ops = diff("ABCD", "AXCY")
    result = apply_diff("ABCD", ops)
    assert result == "AXCY"


def test_minimal_ops():
    """Operations should be minimal based on LCS."""
    ops = diff("ABC", "ABD")
    keeps = sum(1 for op, _ in ops if op == "keep")
    # LCS("ABC", "ABD") = "AB", so 2 keeps
    assert keeps >= 2
