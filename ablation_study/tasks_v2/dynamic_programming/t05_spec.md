# Task: Partition Problem with Constraints

Partition array into k subsets with equal sum, minimizing max subset size.

**Function signature:**
```python
def balanced_partition(arr: list[int], k: int) -> list[list[int]]:
    """
    Partition array into k subsets with equal sum, minimizing max subset size.

    Args:
        arr: List of positive integers
        k: Number of subsets

    Returns:
        List of k subsets (each a list of array indices)
        Returns [] if no valid equal-sum partition exists
    """
    pass
```

**Requirements:**
- All k subsets must have equal sum
- If multiple solutions exist, minimize maximum subset size
- Return indices from original array, not values
- Sum of array must be divisible by k
- Handle impossible partitions (return [])

**Example:**
```python
arr = [1, 2, 3, 4, 5, 6]  # sum = 21
balanced_partition(arr, 3) == [[0, 5], [1, 4], [2, 3]]  # Each sums to 7
# [[1,2], [4], [5]] also valid but less balanced

arr = [1, 2, 3]
balanced_partition(arr, 2) == []  # Sum 6 divisible by 2, but can't partition to 3,3
```

**Difficulty:** Subset sum with balancing constraints
