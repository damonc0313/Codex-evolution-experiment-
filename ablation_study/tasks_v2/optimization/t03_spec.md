# Task: Multi-Objective Knapsack

Maximize value while minimizing weight variance across selected items.

**Function signature:**
```python
def balanced_knapsack(
    capacity: int,
    items: list[tuple[int, int]]  # (weight, value)
) -> tuple[int, float, list[int]]:
    """
    Select items to maximize value while minimizing weight variance.

    Args:
        capacity: Maximum total weight
        items: List of (weight, value) tuples

    Returns:
        Tuple of (total_value, weight_variance, selected_indices)
        Among solutions with max value, pick one with minimum weight variance
    """
    pass
```

**Requirements:**
- Primary objective: maximize total value
- Secondary objective: minimize variance of selected item weights
- Variance = mean of squared deviations from mean weight
- Return indices in sorted order
- Handle empty selection (value=0, variance=0)

**Example:**
```python
items = [(10, 50), (20, 60), (30, 70)]
capacity = 50
# Can select items 0,1 (value=110, weights=[10,20], variance=25)
# Or item 2 (value=70, weights=[30], variance=0)
# Choose 0,1 for higher value
balanced_knapsack(capacity, items) == (110, 25.0, [0, 1])
```

**Difficulty:** Multi-objective optimization
