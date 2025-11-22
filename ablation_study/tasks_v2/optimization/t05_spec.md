# Task: Bin Packing with Item Types

Pack items into bins minimizing bins used, with type compatibility constraints.

**Function signature:**
```python
def typed_bin_packing(
    items: list[tuple[int, str]],  # (size, type)
    bin_capacity: int,
    incompatible: set[tuple[str, str]]  # types that can't share a bin
) -> list[list[int]]:
    """
    Pack items into minimum number of bins respecting type constraints.

    Args:
        items: List of (size, type) for each item
        bin_capacity: Maximum total size per bin
        incompatible: Set of (type1, type2) pairs that can't coexist in same bin

    Returns:
        List of bins, each bin is list of item indices
    """
    pass
```

**Requirements:**
- Minimize number of bins used
- Each bin's total size <= bin_capacity
- No bin contains incompatible types
- Use First Fit Decreasing or similar heuristic
- Return item indices per bin

**Example:**
```python
items = [(5, "A"), (3, "B"), (2, "A"), (4, "C")]
capacity = 10
incompatible = {("A", "B"), ("B", "A")}

# Bin 1: items 0,2 (both type A, size 7)
# Bin 2: items 1 (type B, size 3)
# Bin 3: items 3 (type C, size 4)
# Can also put item 3 in bin 1 if it fits
typed_bin_packing(items, capacity, incompatible) == [[0,2,3], [1]]
```

**Difficulty:** Bin packing with constraints
