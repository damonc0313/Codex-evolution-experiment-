# Task: Longest Common Subsequence with Constraints

Implement a function that finds the longest common subsequence (LCS) between two strings, but with additional constraints.

**Function signature:**
```python
def constrained_lcs(s1: str, s2: str, forbidden_chars: set[str]) -> str:
    """
    Find longest common subsequence, excluding any subsequence containing forbidden characters.

    Args:
        s1: First string
        s2: Second string
        forbidden_chars: Set of characters that cannot appear in result

    Returns:
        Longest common subsequence avoiding forbidden characters
    """
    pass
```

**Requirements:**
- Use dynamic programming
- The result cannot contain any character from forbidden_chars
- If multiple LCS of same length exist, return lexicographically smallest
- Return empty string if no valid LCS exists
- Handle empty strings and empty forbidden set

**Examples:**
```python
constrained_lcs("ABCDEF", "ADBEF", set()) == "ABEF"  # Standard LCS
constrained_lcs("ABCDEF", "ADBEF", {'B'}) == "AEF"   # Skip 'B'
constrained_lcs("ABCDEF", "ADBEF", {'A', 'E', 'F'}) == "D"  # Very constrained
```

**Difficulty:** Dynamic programming with additional constraint tracking
