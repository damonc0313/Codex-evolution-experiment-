import pytest
from solution import pattern_match


def test_literal_match():
    """Exact string match."""
    assert pattern_match("abc", "abc") == True
    assert pattern_match("abc", "xyz") == False


def test_dot_wildcard():
    """Dot matches any character."""
    assert pattern_match("abc", "a.c") == True
    assert pattern_match("aXc", "a.c") == True
    assert pattern_match("ac", "a.c") == False  # Dot must match one char


def test_star_quantifier():
    """Star matches zero or more."""
    assert pattern_match("", "a*") == True  # Zero a's
    assert pattern_match("a", "a*") == True  # One a
    assert pattern_match("aaaa", "a*") == True  # Multiple a's
    assert pattern_match("aabc", "a*bc") == True
    assert pattern_match("bc", "a*bc") == True  # Zero a's


def test_question_quantifier():
    """Question matches zero or one."""
    assert pattern_match("", "a?") == True  # Zero a's
    assert pattern_match("a", "a?") == True  # One a
    assert pattern_match("aa", "a?") == False  # More than one


def test_character_class():
    """Character class matches any listed char."""
    assert pattern_match("a", "[abc]") == True
    assert pattern_match("b", "[abc]") == True
    assert pattern_match("d", "[abc]") == False


def test_character_range():
    """Character class with range."""
    assert pattern_match("a", "[a-z]") == True
    assert pattern_match("m", "[a-z]") == True
    assert pattern_match("z", "[a-z]") == True
    assert pattern_match("A", "[a-z]") == False


def test_combined_patterns():
    """Combine multiple pattern features."""
    assert pattern_match("hello", "h[aeiou]llo") == True
    assert pattern_match("world", "w[a-z]*d") == True
    assert pattern_match("cat", "c[a-z]?t") == True


def test_star_with_class():
    """Star applies to character class."""
    assert pattern_match("abc123", "[a-z]*[0-9]*") == True
    assert pattern_match("", "[a-z]*") == True


def test_must_match_entire():
    """Pattern must match whole text, not substring."""
    assert pattern_match("abc", "ab") == False
    assert pattern_match("abc", "bc") == False
    assert pattern_match("abc", "a.*") == True  # .* matches "bc"


def test_empty_text_and_pattern():
    """Edge cases with empty strings."""
    assert pattern_match("", "") == True
    assert pattern_match("", "a") == False
    assert pattern_match("a", "") == False
    assert pattern_match("", "a*") == True  # Zero a's


def test_greedy_matching():
    """Star is greedy but backtracks if needed."""
    assert pattern_match("aaab", "a*ab") == True
    assert pattern_match("aaa", "a*a") == True


def test_complex_pattern():
    """Realistic complex pattern."""
    # Email-like pattern (simplified)
    pattern = "[a-z]*@[a-z]*.com"
    assert pattern_match("user@example.com", pattern) == True
    assert pattern_match("@.com", pattern) == True  # Degenerate case


def test_multiple_classes():
    """Multiple character classes in pattern."""
    assert pattern_match("a1b2", "[a-z][0-9][a-z][0-9]") == True
    assert pattern_match("ab12", "[a-z][0-9][a-z][0-9]") == False


def test_dot_star():
    """Common .* pattern."""
    assert pattern_match("anything goes", ".*") == True
    assert pattern_match("prefix_something", "prefix.*") == True


def test_question_with_class():
    """Question mark with character class."""
    assert pattern_match("a1", "[a-z][0-9]?") == True
    assert pattern_match("a", "[a-z][0-9]?") == True
    assert pattern_match("a12", "[a-z][0-9]?") == False
