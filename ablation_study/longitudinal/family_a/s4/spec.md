# Session 4: Diff Algorithm

## Task
Use LCS concepts to implement a diff algorithm that shows edits.

## Function Signature
```python
def diff(s1: str, s2: str) -> list[tuple[str, str]]:
    """
    Compute diff operations to transform s1 into s2.

    Args:
        s1: Source string
        s2: Target string

    Returns:
        List of operations:
        - ("keep", char): char is in both, keep it
        - ("del", char): char in s1 only, delete it
        - ("add", char): char in s2 only, add it
    """
```

## Requirements
- Operations should be minimal (based on LCS)
- Applied in order, operations transform s1 to s2
- Use LCS to identify "keep" operations

## Examples
```python
diff("ABC", "ABD") == [
    ("keep", "A"),
    ("keep", "B"),
    ("del", "C"),
    ("add", "D")
]

diff("ABC", "ABC") == [
    ("keep", "A"),
    ("keep", "B"),
    ("keep", "C")
]
```

## Learning Transfer
Direct application of LCS: common subsequence = keep operations,
differences = add/delete operations.
