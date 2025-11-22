def constrained_lcs(s1: str, s2: str, forbidden_chars: set[str]) -> str:
    """
    Find longest common subsequence, excluding any subsequence containing forbidden characters.

    Args:
        s1: First string
        s2: Second string
        forbidden_chars: Set of characters that cannot appear in result

    Returns:
        Longest common subsequence avoiding forbidden characters
    """
    if not s1 or not s2:
        return ""

    n, m = len(s1), len(s2)

    # DP table: dp[i][j] = lexicographically smallest LCS string for s1[0:i] and s2[0:j]
    # Store actual strings to handle lexicographic ordering
    dp = [["" for _ in range(m + 1)] for _ in range(n + 1)]

    # Fill DP table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            char1 = s1[i-1]
            char2 = s2[j-1]

            if char1 == char2 and char1 not in forbidden_chars:
                # Characters match and not forbidden - extend LCS
                dp[i][j] = dp[i-1][j-1] + char1
            else:
                # Choose longer LCS, or lexicographically smaller if same length
                left = dp[i][j-1]
                top = dp[i-1][j]
                if len(left) > len(top):
                    dp[i][j] = left
                elif len(top) > len(left):
                    dp[i][j] = top
                else:
                    # Same length - choose lexicographically smaller
                    dp[i][j] = min(left, top)

    return dp[n][m]
