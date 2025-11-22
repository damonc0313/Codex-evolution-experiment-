# Session 2: Constrained LCS

## Task
Extend LCS to require that the result must contain all characters from a required set.

## Function Signature
```python
def constrained_lcs(s1: str, s2: str, must_include: str) -> str:
    """
    Find LCS that must contain all characters from must_include.

    Args:
        s1: First string
        s2: Second string
        must_include: Characters that must appear in result

    Returns:
        Longest common subsequence containing all required chars,
        or "" if impossible
    """
```

## Requirements
- Build on basic LCS algorithm
- Additional constraint tracking for required characters
- Return "" if no valid LCS exists

## Examples
```python
constrained_lcs("ABCDEF", "AEBDF", "AD") == "ABDF"  # Contains A and D
constrained_lcs("ABCDEF", "AEBDF", "XY") == ""      # X,Y not in both
constrained_lcs("ABC", "ABC", "") == "ABC"          # No constraint
```

## Learning Transfer
Uses Session 1's DP approach with additional constraint tracking.
