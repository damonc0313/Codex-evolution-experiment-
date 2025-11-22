# Session 5: Sequence Alignment (Needleman-Wunsch)

## Task
Implement the full Needleman-Wunsch sequence alignment algorithm with scoring.

## Function Signature
```python
def align(s1: str, s2: str, match: int = 1, mismatch: int = -1, gap: int = -1) -> tuple[int, str, str]:
    """
    Global sequence alignment with custom scoring.

    Args:
        s1: First sequence
        s2: Second sequence
        match: Score for matching characters (positive)
        mismatch: Score for mismatching characters (negative)
        gap: Score for gaps/insertions (negative)

    Returns:
        Tuple of (score, aligned_s1, aligned_s2)
        Aligned strings may contain '-' for gaps
    """
```

## Requirements
- Use dynamic programming (similar to LCS but with scoring)
- Handle gaps (insertions/deletions) with gap penalty
- Return the optimal alignment with score

## Examples
```python
align("AGTC", "AGTC") == (4, "AGTC", "AGTC")  # Perfect match
align("AGT", "ACT") == (1, "AGT", "ACT")       # 2 match + 1 mismatch
align("AC", "ABC") == (1, "A-C", "ABC")        # Gap needed
```

## Learning Transfer
Culmination of LCS concepts:
- DP table from Session 1
- Constraint handling from Session 2
- Multiple alignment from Session 3
- Edit operations from Session 4
All combine into sequence alignment.
