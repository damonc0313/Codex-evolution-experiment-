# Task: Matrix Chain Multiplication

Find optimal parenthesization for matrix chain multiplication.

**Function signature:**
```python
def matrix_chain_order(dimensions: list[int]) -> tuple[int, str]:
    """
    Find minimum number of scalar multiplications needed and optimal parenthesization.

    Args:
        dimensions: List where matrix i has dimensions[i-1] × dimensions[i]
                   For n matrices, dimensions has length n+1

    Returns:
        Tuple of (min_operations, parenthesization_string)
        e.g., ((A0(A1A2))A3)
    """
    pass
```

**Requirements:**
- Use dynamic programming
- Return both minimum operations count and parenthesization
- Parenthesization format: ((A0(A1A2))A3) for matrices indexed 0-3
- Handle 1 matrix (0 multiplications)
- Empty input should return (0, "")

**Example:**
```python
# Matrices: 10×20, 20×30, 30×40
dims = [10, 20, 30, 40]
matrix_chain_order(dims) == (18000, "((A0A1)A2)")
# vs (24000, "(A0(A1A2))")
```

**Difficulty:** Classic DP with backtracking for reconstruction
