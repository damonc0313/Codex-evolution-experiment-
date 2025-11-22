# Task: Edit Distance with Custom Costs

Implement edit distance (Levenshtein) with custom operation costs.

**Function signature:**
```python
def custom_edit_distance(
    s1: str,
    s2: str,
    costs: dict[str, int] = None  # {"insert": 1, "delete": 1, "replace": 1}
) -> tuple[int, list[str]]:
    """
    Compute minimum edit distance with custom operation costs and return operations.

    Args:
        s1: Source string
        s2: Target string
        costs: Dict of operation costs (defaults to 1 each if None)

    Returns:
        Tuple of (min_cost, list_of_operations)
        Operations: ["insert:c", "delete:c", "replace:a->b", "match:c"]
    """
    pass
```

**Requirements:**
- Use dynamic programming with backtracking
- Default costs are 1 for each operation if not specified
- Match operation has cost 0
- Return both minimum cost and sequence of operations
- Operations list should transform s1 into s2
- Handle empty strings

**Example:**
```python
custom_edit_distance("kitten", "sitting") == (3, [...operations...])
custom_edit_distance("", "abc") == (3, ["insert:a", "insert:b", "insert:c"])
custom_edit_distance("abc", "", {"delete": 2}) == (6, ["delete:a", "delete:b", "delete:c"])
```

**Difficulty:** DP with backtracking and custom costs
