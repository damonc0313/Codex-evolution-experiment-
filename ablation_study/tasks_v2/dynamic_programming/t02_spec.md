# Task: Bounded Knapsack with Item Dependencies

Implement a function that solves a knapsack problem where items have dependencies.

**Function signature:**
```python
def dependent_knapsack(
    capacity: int,
    items: list[dict]  # {"weight": int, "value": int, "requires": list[int]}
) -> tuple[int, list[int]]:
    """
    Solve knapsack where items may require other items to be included.

    Args:
        capacity: Maximum weight capacity
        items: List of items with weight, value, and list of required item indices

    Returns:
        Tuple of (max_value, list_of_selected_indices)
    """
    pass
```

**Requirements:**
- Use dynamic programming
- If item i is selected, all items in items[i]["requires"] must also be selected
- Dependencies are acyclic (guaranteed)
- Maximize total value without exceeding capacity
- Return indices of selected items in sorted order
- Handle empty items list and zero capacity

**Example:**
```python
items = [
    {"weight": 2, "value": 10, "requires": []},       # Item 0
    {"weight": 3, "value": 15, "requires": [0]},      # Item 1 requires 0
    {"weight": 1, "value": 5, "requires": []}         # Item 2
]
dependent_knapsack(5, items) == (20, [0, 1, 2])  # Total weight=6 exceeds, so (15, [0,1])
dependent_knapsack(6, items) == (30, [0, 1, 2])  # All items fit
```

**Difficulty:** DP with dependency constraints
