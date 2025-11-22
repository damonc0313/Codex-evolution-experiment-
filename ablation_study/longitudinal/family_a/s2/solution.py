"""
Session 2: Constrained LCS
Extends basic LCS to require that result contains all characters from a required set.
"""
from collections import Counter
from functools import lru_cache


def constrained_lcs(s1: str, s2: str, must_include: str) -> str:
    """
    Find LCS that must contain all characters from must_include.

    Args:
        s1: First string
        s2: Second string
        must_include: Characters that must appear in result

    Returns:
        Longest common subsequence containing all required chars,
        or "" if impossible
    """
    required = Counter(must_include)

    # Check feasibility: all required chars must exist in both strings
    # with sufficient count
    s1_count = Counter(s1)
    s2_count = Counter(s2)
    for c, cnt in required.items():
        if s1_count[c] < cnt or s2_count[c] < cnt:
            return ""

    # Handle empty strings
    if not s1 or not s2:
        return "" if not required else ""

    def counter_to_tuple(c):
        """Convert Counter to hashable tuple for memoization."""
        return tuple(sorted(c.items()))

    def tuple_to_counter(t):
        """Convert tuple back to Counter."""
        return Counter(dict(t))

    @lru_cache(maxsize=None)
    def dp(i, j, remaining_tuple):
        """
        Find longest LCS of s1[:i] and s2[:j] containing all chars in remaining.

        Returns the LCS string or None if impossible.
        """
        # Base case: one or both strings exhausted
        if i == 0 or j == 0:
            if not remaining_tuple:  # All requirements satisfied
                return ""
            return None  # Requirements not satisfiable

        remaining = tuple_to_counter(remaining_tuple)
        best = None

        # Option 1: skip s1[i-1]
        res = dp(i - 1, j, remaining_tuple)
        if res is not None:
            if best is None or len(res) > len(best):
                best = res

        # Option 2: skip s2[j-1]
        res = dp(i, j - 1, remaining_tuple)
        if res is not None:
            if best is None or len(res) > len(best):
                best = res

        # Option 3: include character if s1[i-1] == s2[j-1]
        if s1[i - 1] == s2[j - 1]:
            c = s1[i - 1]
            new_remaining = remaining.copy()
            if c in new_remaining:
                new_remaining[c] -= 1
                if new_remaining[c] == 0:
                    del new_remaining[c]
            new_remaining_tuple = counter_to_tuple(new_remaining)

            res = dp(i - 1, j - 1, new_remaining_tuple)
            if res is not None:
                candidate = res + c
                if best is None or len(candidate) > len(best):
                    best = candidate

        return best

    result = dp(len(s1), len(s2), counter_to_tuple(required))
    return result if result is not None else ""
