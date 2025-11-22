# Session 3: Multiple String LCS

## Task
Generalize LCS to work with multiple strings (not just two).

## Function Signature
```python
def multi_lcs(strings: list[str]) -> str:
    """
    Find longest common subsequence of all input strings.

    Args:
        strings: List of strings (at least 1)

    Returns:
        Longest subsequence common to ALL strings
    """
```

## Requirements
- Handle arbitrary number of strings
- Generalize the DP approach to N dimensions (or use pairwise reduction)
- Efficient enough for small inputs (up to 5 strings of length 20)

## Examples
```python
multi_lcs(["ABC"]) == "ABC"
multi_lcs(["ABCD", "ABDC"]) == "ABD" or "ABC"
multi_lcs(["ABC", "BCA", "CAB"]) == "A" or "B" or "C"
multi_lcs(["XYZ", "ABC"]) == ""
```

## Learning Transfer
Extends 2-string LCS to N strings. Can use:
1. N-dimensional DP table
2. Pairwise reduction: LCS(s1, LCS(s2, s3...))
