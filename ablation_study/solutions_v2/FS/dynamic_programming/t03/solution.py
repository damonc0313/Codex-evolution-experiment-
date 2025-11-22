def custom_edit_distance(
    s1: str,
    s2: str,
    costs: dict[str, int] = None
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
    # Default costs
    if costs is None:
        costs = {}
    insert_cost = costs.get("insert", 1)
    delete_cost = costs.get("delete", 1)
    replace_cost = costs.get("replace", 1)

    m, n = len(s1), len(s2)

    # DP table: dp[i][j] = min cost to transform s1[:i] to s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases
    # Transform s1[:i] to empty string -> delete all
    for i in range(1, m + 1):
        dp[i][0] = dp[i-1][0] + delete_cost

    # Transform empty to s2[:j] -> insert all
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j-1] + insert_cost

    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                # Match - no cost
                dp[i][j] = dp[i-1][j-1]
            else:
                # Min of insert, delete, replace
                dp[i][j] = min(
                    dp[i][j-1] + insert_cost,    # Insert s2[j-1]
                    dp[i-1][j] + delete_cost,    # Delete s1[i-1]
                    dp[i-1][j-1] + replace_cost  # Replace s1[i-1] with s2[j-1]
                )

    # Backtrack to find operations
    operations = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
            # Match
            operations.append(f"match:{s1[i-1]}")
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + replace_cost:
            # Replace
            operations.append(f"replace:{s1[i-1]}->{s2[j-1]}")
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + insert_cost:
            # Insert
            operations.append(f"insert:{s2[j-1]}")
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + delete_cost:
            # Delete
            operations.append(f"delete:{s1[i-1]}")
            i -= 1
        else:
            # This should not happen if DP is correct, but handle gracefully
            break

    # Reverse to get operations in correct order (from start to end)
    operations.reverse()

    return dp[m][n], operations
