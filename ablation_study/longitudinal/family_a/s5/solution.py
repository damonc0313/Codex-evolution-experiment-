def align(s1: str, s2: str, match: int = 1, mismatch: int = -1, gap: int = -1) -> tuple[int, str, str]:
    """
    Global sequence alignment with custom scoring (Needleman-Wunsch algorithm).

    Args:
        s1: First sequence
        s2: Second sequence
        match: Score for matching characters (positive)
        mismatch: Score for mismatching characters (negative)
        gap: Score for gaps/insertions (negative)

    Returns:
        Tuple of (score, aligned_s1, aligned_s2)
        Aligned strings may contain '-' for gaps
    """
    n, m = len(s1), len(s2)

    # Initialize DP table
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Initialize first column (gaps in s2)
    for i in range(n + 1):
        dp[i][0] = i * gap

    # Initialize first row (gaps in s1)
    for j in range(m + 1):
        dp[0][j] = j * gap

    # Fill the DP table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Score for match/mismatch (coming from diagonal)
            if s1[i - 1] == s2[j - 1]:
                diag_score = dp[i - 1][j - 1] + match
            else:
                diag_score = dp[i - 1][j - 1] + mismatch

            # Score for gap in s2 (coming from above)
            up_score = dp[i - 1][j] + gap

            # Score for gap in s1 (coming from left)
            left_score = dp[i][j - 1] + gap

            dp[i][j] = max(diag_score, up_score, left_score)

    # Traceback to construct alignment
    aligned_s1 = []
    aligned_s2 = []
    i, j = n, m

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            # Check if we came from diagonal (match/mismatch)
            if s1[i - 1] == s2[j - 1]:
                diag_score = dp[i - 1][j - 1] + match
            else:
                diag_score = dp[i - 1][j - 1] + mismatch

            if dp[i][j] == diag_score:
                aligned_s1.append(s1[i - 1])
                aligned_s2.append(s2[j - 1])
                i -= 1
                j -= 1
                continue

        if i > 0 and dp[i][j] == dp[i - 1][j] + gap:
            # Gap in s2
            aligned_s1.append(s1[i - 1])
            aligned_s2.append('-')
            i -= 1
        elif j > 0:
            # Gap in s1
            aligned_s1.append('-')
            aligned_s2.append(s2[j - 1])
            j -= 1
        else:
            # Edge case: i > 0 but we couldn't match gap
            aligned_s1.append(s1[i - 1])
            aligned_s2.append('-')
            i -= 1

    # Reverse since we built from end to start
    aligned_s1.reverse()
    aligned_s2.reverse()

    return dp[n][m], ''.join(aligned_s1), ''.join(aligned_s2)
