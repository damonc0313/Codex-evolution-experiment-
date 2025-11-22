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
    m, n = len(s1), len(s2)

    # Build LCS DP table
    # dp[i][j] = length of LCS of s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to generate diff operations
    # We traverse from the end and build operations in reverse
    ops = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            # Characters match - keep operation
            ops.append(("keep", s1[i - 1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            # Character in s2 only - add operation
            ops.append(("add", s2[j - 1]))
            j -= 1
        else:
            # Character in s1 only - delete operation
            ops.append(("del", s1[i - 1]))
            i -= 1

    # Reverse to get correct order
    ops.reverse()
    return ops
