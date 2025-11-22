"""
Session 3: Multiple String LCS

Generalizes the classic 2-string LCS to work with arbitrary number of strings
using pairwise reduction: LCS(s1, s2, s3, ...) = LCS(s1, LCS(s2, s3, ...))
"""


def lcs_two(s1: str, s2: str) -> str:
    """
    Find longest common subsequence of two strings using DP.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Longest common subsequence
    """
    if not s1 or not s2:
        return ""

    m, n = len(s1), len(s2)

    # DP table: dp[i][j] = length of LCS of s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to reconstruct the LCS
    result = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return ''.join(reversed(result))


def multi_lcs(strings: list[str]) -> str:
    """
    Find longest common subsequence of all input strings.

    Uses pairwise reduction: compute LCS of first two strings,
    then LCS of that result with third string, and so on.

    Args:
        strings: List of strings (at least 1)

    Returns:
        Longest subsequence common to ALL strings
    """
    if not strings:
        return ""

    # Handle empty string case - if any string is empty, result is empty
    if any(s == "" for s in strings):
        return ""

    # Start with first string and reduce pairwise
    result = strings[0]

    for i in range(1, len(strings)):
        result = lcs_two(result, strings[i])
        # Early termination if result becomes empty
        if not result:
            return ""

    return result
