import pytest
from solution import custom_edit_distance


def test_basic_edit_distance():
    """Classic kitten->sitting example."""
    cost, ops = custom_edit_distance("kitten", "sitting")
    assert cost == 3
    # Operations should transform kitten to sitting
    assert len(ops) > 0


def test_empty_to_string():
    """Insert all characters."""
    cost, ops = custom_edit_distance("", "abc")
    assert cost == 3
    assert ops == ["insert:a", "insert:b", "insert:c"]


def test_string_to_empty():
    """Delete all characters."""
    cost, ops = custom_edit_distance("abc", "")
    assert cost == 3
    assert all("delete" in op for op in ops)


def test_identical_strings():
    """No edits needed."""
    cost, ops = custom_edit_distance("hello", "hello")
    assert cost == 0
    assert all("match" in op for op in ops)


def test_custom_costs():
    """Higher delete cost."""
    cost1, _ = custom_edit_distance("abc", "", {"delete": 2})
    assert cost1 == 6  # 3 deletes at cost 2


def test_replace_vs_insert_delete():
    """Replacement might be cheaper."""
    cost, ops = custom_edit_distance("a", "b", {"replace": 1})
    assert cost == 1
    assert "replace:a->b" in ops


def test_operations_correctness():
    """Verify operations actually transform s1 to s2."""
    s1, s2 = "abc", "aec"
    cost, ops = custom_edit_distance(s1, s2)
    # Should have replace:b->e operation
    assert cost == 1
    assert any("replace" in op and "b" in op and "e" in op for op in ops)


def test_single_char_strings():
    """Edge case single characters."""
    cost, ops = custom_edit_distance("a", "b")
    assert cost == 1


def test_long_strings():
    """Performance on longer inputs."""
    s1 = "a" * 100
    s2 = "b" * 100
    cost, ops = custom_edit_distance(s1, s2)
    assert cost == 100  # All replaces
