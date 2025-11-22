def matrix_chain_order(dimensions: list[int]) -> tuple[int, str]:
    """
    Find minimum number of scalar multiplications needed and optimal parenthesization.

    Args:
        dimensions: List where matrix i has dimensions[i-1] x dimensions[i]
                   For n matrices, dimensions has length n+1

    Returns:
        Tuple of (min_operations, parenthesization_string)
        e.g., ((A0(A1A2))A3)
    """
    # Handle edge cases
    if len(dimensions) == 0:
        return (0, "")

    n = len(dimensions) - 1  # Number of matrices

    if n == 0:
        return (0, "")

    if n == 1:
        return (0, "A0")

    # m[i][j] = minimum number of scalar multiplications to compute A_i...A_j
    # Using 1-indexed matrices internally for cleaner DP
    m = [[0] * (n + 1) for _ in range(n + 1)]

    # s[i][j] = optimal split point k for computing A_i...A_j
    s = [[0] * (n + 1) for _ in range(n + 1)]

    # l is the chain length
    for l in range(2, n + 1):  # l = 2, 3, ..., n
        for i in range(1, n - l + 2):  # i = 1, 2, ..., n-l+1
            j = i + l - 1
            m[i][j] = float('inf')

            # Try all possible split points
            for k in range(i, j):
                # Cost = cost of computing A_i...A_k + cost of A_{k+1}...A_j
                #      + cost of multiplying the two resulting matrices
                cost = m[i][k] + m[k + 1][j] + dimensions[i - 1] * dimensions[k] * dimensions[j]

                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k

    # Reconstruct the optimal parenthesization
    def build_parenthesization(i: int, j: int) -> str:
        if i == j:
            return f"A{i - 1}"  # Convert to 0-indexed for output
        else:
            k = s[i][j]
            left = build_parenthesization(i, k)
            right = build_parenthesization(k + 1, j)
            return f"({left}{right})"

    paren = build_parenthesization(1, n)

    return (m[1][n], paren)
