# Session 1: Basic LCS

## Task
Implement the classic Longest Common Subsequence algorithm.

## Function Signature
```python
def lcs(s1: str, s2: str) -> str:
    """
    Find the longest common subsequence of two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        The longest common subsequence (if multiple, return any)
    """
```

## Requirements
- Use dynamic programming
- O(n*m) time complexity
- Return the actual subsequence string, not just length

## Examples
```python
lcs("ABCDEF", "AEBDF") == "ABDF"  # or any valid LCS of length 4
lcs("ABC", "XYZ") == ""
lcs("HELLO", "HELLO") == "HELLO"
```

## Learning Goal
Understand DP table construction and backtracking for sequence problems.
